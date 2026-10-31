import sys
import logging
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, BackgroundTasks, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, OTPCode, DeviceSession
from app.schemas.auth import (
    SignupRequest, VerifySignupOTPRequest,
    LoginRequest, VerifyLoginOTPRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.utils.otp import generate_otp
from app.services.email_service import EmailService

logger = logging.getLogger("uvicorn.error")

# Hardware Device Concurrency Limit: Maximum 2 Computers and 1 Mobile Phone per User
DEVICE_LIMITS = {
    "computer": 2,
    "phone": 1
}

class AuthService:

    # --- Common Helper: Generate OTP, Persist to Database & Dispatch via BackgroundTasks ---
    @staticmethod
    def _send_otp(
        db: Session,
        email: str,
        user_name: str,
        purpose: str,
        subject: str,
        background_tasks: BackgroundTasks
    ) -> str:
        # Invalidate any existing active OTP for this purpose
        db.execute(delete(OTPCode).where(OTPCode.email == email, OTPCode.purpose == purpose))
        
        otp = generate_otp(6)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        db_otp = OTPCode(email=email, otp_code=otp, purpose=purpose, expires_at=expires_at)
        db.add(db_otp)
        db.commit()

        # 1. Output safe diagnostic banner to stdout (cp1252 / Windows safe)
        banner = (
            f"\n"
            f"======================================================\n"
            f">> [LIVE OTP CODE] Purpose: {purpose.upper()}\n"
            f">> Target Email:   {email}\n"
            f">> YOUR OTP IS:    >>>  {otp}  <<<\n"
            f">> Valid For:      {settings.OTP_EXPIRE_MINUTES} minutes\n"
            f"======================================================\n"
        )
        try:
            print(banner, flush=True)
        except Exception:
            sys.stdout.write(banner.encode("ascii", errors="replace").decode("ascii"))
            sys.stdout.flush()

        # 2. Queue asynchronous email delivery via FastAPI BackgroundTasks
        msg = f"Your {subject} verification code is: {otp}. This code is valid for {settings.OTP_EXPIRE_MINUTES} minutes. (আপনার ওটিপি কোড হলো: {otp})"
        background_tasks.add_task(EmailService.send_welcome_email, email, subject, user_name, msg)

        return otp

    # --- Common Helper: Validate OTP Existence and Expiration Window ---
    @staticmethod
    def _verify_otp_record(db: Session, email: str, otp_code: str, purpose: str) -> None:
        stmt = select(OTPCode).where(
            OTPCode.email == email,
            OTPCode.otp_code == otp_code,
            OTPCode.purpose == purpose
        )
        record = db.scalar(stmt)
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code.")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        exp = record.expires_at.replace(tzinfo=None)
        if now > exp:
            db.delete(record)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired.")

        # Invalidate OTP record immediately upon successful consumption (Strict Single-Use)
        db.delete(record)
        db.commit()


    # ================= 1. User Registration Flow (Signup with 2FA OTP) =================
    @staticmethod
    def signup(db: Session, payload: SignupRequest, background_tasks: BackgroundTasks):
        existing_user = db.scalar(select(User).where(User.email == payload.email))
        if existing_user and existing_user.is_verified:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        if existing_user and not existing_user.is_verified:
            # Update credentials for unverified existing profile
            existing_user.name = payload.name
            existing_user.address = payload.address
            existing_user.hashed_password = hash_password(payload.password)
            db.commit()
            user = existing_user
        else:
            # Create new unverified user entity
            user = User(
                name=payload.name,
                email=payload.email,
                address=payload.address,
                hashed_password=hash_password(payload.password),
                is_verified=False
            )
            db.add(user)
            db.commit()

        otp = AuthService._send_otp(db, user.email, user.name, "signup", "Account Signup OTP", background_tasks)
        return {
            "status": "otp_sent",
            "message": f"Verification OTP sent to {user.email}.",
            "dev_otp": otp
        }

    @staticmethod
    def verify_signup(db: Session, payload: VerifySignupOTPRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "signup")
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        user.is_verified = True
        db.commit()
        return {"status": "verified", "message": "Congratulations! Your account has been verified successfully."}


    # ================= 2. Authentication Flow with Device Session Concurrency =================
    @staticmethod
    def login(db: Session, payload: LoginRequest, background_tasks: BackgroundTasks):
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if not user.is_verified:
            raise HTTPException(status_code=403, detail="Account unverified. Please complete OTP verification.")

        # Password matched: Dispatch 2FA OTP instead of direct token issuance
        otp = AuthService._send_otp(db, user.email, user.name, "login", f"Login Verification OTP ({datetime.now().strftime('%H:%M:%S')})", background_tasks)
        return {
            "status": "otp_required",
            "message": "Password verified! Please submit the OTP sent to your email to complete login.",
            "dev_otp": otp
        }

    @staticmethod
    def verify_login(db: Session, payload: VerifyLoginOTPRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "login")
        user = db.scalar(select(User).where(User.email == payload.email))

        # --- Enforce Multi-Device Limits: Max 2 Computers, 1 Phone per User ---
        stmt = (
            select(DeviceSession)
            .where(
                DeviceSession.user_id == user.id,
                DeviceSession.device_type == payload.device_type,
                DeviceSession.is_active == True
            )
            .order_by(DeviceSession.created_at.asc())  # Oldest active sessions first (FIFO)
        )
        active_sessions = list(db.scalars(stmt).all())
        max_allowed = DEVICE_LIMITS[payload.device_type]

        logged_out_msg = ""
        if len(active_sessions) >= max_allowed:
            # Threshold exceeded: Evict oldest device sessions (First-In, First-Out)
            to_logout = active_sessions[: len(active_sessions) - max_allowed + 1]
            for old_session in to_logout:
                old_session.is_active = False
            logged_out_msg = f" (Device limit reached: Oldest {payload.device_type} session has been automatically logged out.)"

        # Register new active device session
        new_session = DeviceSession(
            user_id=user.id,
            device_type=payload.device_type,
            device_name=payload.device_name,
            is_active=True
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # Issue cryptographically signed JWT bearer token
        token = create_access_token(user_id=user.id, session_id=new_session.id)
        return {
            "status": "login_success",
            "message": f"Login successful!{logged_out_msg}",
            "access_token": token,
            "token_type": "bearer",
            "device_info": f"{payload.device_type} ({payload.device_name})"
        }


    # ================= 3. Password Recovery Flow (Forgot & Reset with OTP) =================
    @staticmethod
    def forgot_password(db: Session, payload: ForgotPasswordRequest, background_tasks: BackgroundTasks):
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user:
            raise HTTPException(status_code=404, detail="No account registered with this email.")

        otp = AuthService._send_otp(db, user.email, user.name, "forgot", "Password Reset OTP", background_tasks)
        return {
            "status": "otp_sent",
            "message": "Password reset OTP has been sent to your email address.",
            "dev_otp": otp
        }

    @staticmethod
    def reset_password(db: Session, payload: ResetPasswordRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "forgot")
        user = db.scalar(select(User).where(User.email == payload.email))
        
        # Hash new password with Argon2id and update profile
        user.hashed_password = hash_password(payload.new_password)
        
        # Invalidate all active device sessions upon password reset for security
        stmt = select(DeviceSession).where(DeviceSession.user_id == user.id, DeviceSession.is_active == True)
        for s in db.scalars(stmt).all():
            s.is_active = False

        db.commit()
        return {"status": "password_reset", "message": "Password changed successfully. Please log in with your new password."}
