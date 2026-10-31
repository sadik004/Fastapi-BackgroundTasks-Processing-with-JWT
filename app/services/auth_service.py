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

# ডিভাইস লিমিট রুল: সর্বোচ্চ ২টি কম্পিউটার এবং ১টি ফোন
DEVICE_LIMITS = {
    "computer": 2,
    "phone": 1
}

class AuthService:

    # --- কমন হেল্পার: ওটিপি তৈরি, ডাটাবেজে সেভ এবং ইমেইলে পাঠানো ---
    @staticmethod
    def _send_otp(
        db: Session,
        email: str,
        user_name: str,
        purpose: str,
        subject: str,
        background_tasks: BackgroundTasks
    ) -> str:
        # আগের কোনো পুরনো ওটিপি থাকলে মুছে ফেলা
        db.execute(delete(OTPCode).where(OTPCode.email == email, OTPCode.purpose == purpose))
        
        otp = generate_otp(6)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        db_otp = OTPCode(email=email, otp_code=otp, purpose=purpose, expires_at=expires_at)
        db.add(db_otp)
        db.commit()

        # ১. সরাসরি টার্মিনাল আউটপুটে (stdout) সেফ প্রিন্ট (Windows cp1252 কমপ্যাটিবল)
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

        # ২. ব্যাকগ্রাউন্ডে আসল ইমেইল কিউতে দিয়ে দেওয়া
        msg = f"আপনার {subject}-এর ওটিপি কোড হলো: {otp}। এটি {settings.OTP_EXPIRE_MINUTES} মিনিট কার্যকর থাকবে।"
        background_tasks.add_task(EmailService.send_welcome_email, email, subject, user_name, msg)

        return otp

    # --- কমন হেল্পার: ওটিপি সঠিক ও মেয়াদ আছে কি না তা চেক করা ---
    @staticmethod
    def _verify_otp_record(db: Session, email: str, otp_code: str, purpose: str) -> None:
        stmt = select(OTPCode).where(
            OTPCode.email == email,
            OTPCode.otp_code == otp_code,
            OTPCode.purpose == purpose
        )
        record = db.scalar(stmt)
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ভুল ওটিপি কোড!")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        exp = record.expires_at.replace(tzinfo=None)
        if now > exp:
            db.delete(record)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ওটিপির মেয়াদ শেষ হয়ে গেছে!")

        # ওটিপি সফলভাবে ব্যবহার হওয়ার পর মুছে ফেলা (One-Time Use)
        db.delete(record)
        db.commit()


    # ================= ১. সাইনআপ (Signup with OTP) =================
    @staticmethod
    def signup(db: Session, payload: SignupRequest, background_tasks: BackgroundTasks):
        existing_user = db.scalar(select(User).where(User.email == payload.email))
        if existing_user and existing_user.is_verified:
            raise HTTPException(status_code=400, detail="এই ইমেইলে আগেই অ্যাকাউন্ট খোলা আছে!")

        if existing_user and not existing_user.is_verified:
            # আগে সাইনআপ করে ভেরিফাই না করে থাকলে তথ্য আপডেট করা
            existing_user.name = payload.name
            existing_user.address = payload.address
            existing_user.hashed_password = hash_password(payload.password)
            db.commit()
            user = existing_user
        else:
            # নতুন ইউজার তৈরি (is_verified=False অবস্থায়)
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
            "message": f"{user.email}-এ সাইনআপ ওটিপি পাঠানো হয়েছে।",
            "dev_otp": otp
        }

    @staticmethod
    def verify_signup(db: Session, payload: VerifySignupOTPRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "signup")
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user:
            raise HTTPException(status_code=404, detail="ইউজার পাওয়া যায়নি!")
        
        user.is_verified = True
        db.commit()
        return {"status": "verified", "message": "অভিনন্দন! আপনার অ্যাকাউন্ট সফলভাবে ভেরিফাই ও চালু হয়েছে।"}


    # ================= ২. লগইন ও ডিভাইস লিমিট (Login with OTP) =================
    @staticmethod
    def login(db: Session, payload: LoginRequest, background_tasks: BackgroundTasks):
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="ইমেইল বা পাসওয়ার্ড ভুল!")

        if not user.is_verified:
            raise HTTPException(status_code=403, detail="আপনার অ্যাকাউন্ট এখনও ওটিপি দিয়ে ভেরিফাই করা হয়নি!")

        # পাসওয়ার্ড মিলেছে, কিন্তু টোকেন না দিয়ে আগে ওটিপি পাঠানো হচ্ছে
        otp = AuthService._send_otp(db, user.email, user.name, "login", f"Login Verification OTP ({datetime.now().strftime('%H:%M:%S')})", background_tasks)
        return {
            "status": "otp_required",
            "message": "পাসওয়ার্ড সঠিক! লগইন সম্পন্ন করতে ইমেইলে যাওয়া ওটিপি দিন।",
            "dev_otp": otp
        }

    @staticmethod
    def verify_login(db: Session, payload: VerifyLoginOTPRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "login")
        user = db.scalar(select(User).where(User.email == payload.email))

        # --- ২টি কম্পিউটার ও ১টি ফোন লিমিট চেক করার আসল লজিক ---
        stmt = (
            select(DeviceSession)
            .where(
                DeviceSession.user_id == user.id,
                DeviceSession.device_type == payload.device_type,
                DeviceSession.is_active == True
            )
            .order_by(DeviceSession.created_at.asc())  # সবচেয়ে পুরনো লগইন সবার আগে থাকবে
        )
        active_sessions = list(db.scalars(stmt).all())
        max_allowed = DEVICE_LIMITS[payload.device_type]

        logged_out_msg = ""
        if len(active_sessions) >= max_allowed:
            # লিমিট ছাড়িয়ে গেছে! সবচেয়ে পুরনো ডিভাইসগুলোকে অটো-লগআউট (is_active=False) করে দেওয়া হচ্ছে
            to_logout = active_sessions[: len(active_sessions) - max_allowed + 1]
            for old_session in to_logout:
                old_session.is_active = False
            logged_out_msg = f" (লিমিট অতিক্রম করায় আপনার পুরনো {payload.device_type} লগআউট করে দেওয়া হয়েছে!)"

        # নতুন ডিভাইস সেশন ডাটাবেজে যোগ করা
        new_session = DeviceSession(
            user_id=user.id,
            device_type=payload.device_type,
            device_name=payload.device_name,
            is_active=True
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # আসল JWT টোকেন তৈরি
        token = create_access_token(user_id=user.id, session_id=new_session.id)
        return {
            "status": "login_success",
            "message": f"লগইন সফল হয়েছে!{logged_out_msg}",
            "access_token": token,
            "token_type": "bearer",
            "device_info": f"{payload.device_type} ({payload.device_name})"
        }


    # ================= ৩. ফরগট পাসওয়ার্ড (Forgot Password with OTP) =================
    @staticmethod
    def forgot_password(db: Session, payload: ForgotPasswordRequest, background_tasks: BackgroundTasks):
        user = db.scalar(select(User).where(User.email == payload.email))
        if not user:
            raise HTTPException(status_code=404, detail="এই ইমেইলে কোনো অ্যাকাউন্ট পাওয়া যায়নি!")

        otp = AuthService._send_otp(db, user.email, user.name, "forgot", "Password Reset OTP", background_tasks)
        return {
            "status": "otp_sent",
            "message": "পাসওয়ার্ড রিসেট করার জন্য আপনার ইমেইলে ওটিপি পাঠানো হয়েছে।",
            "dev_otp": otp
        }

    @staticmethod
    def reset_password(db: Session, payload: ResetPasswordRequest):
        AuthService._verify_otp_record(db, payload.email, payload.otp_code, "forgot")
        user = db.scalar(select(User).where(User.email == payload.email))
        
        # নতুন পাসওয়ার্ড Argon2 দিয়ে লক করে সেভ করা
        user.hashed_password = hash_password(payload.new_password)
        
        # পাসওয়ার্ড রিসেট হলে নিরাপত্তার জন্য সব পুরনো ডিভাইস সেশন লগআউট করে দেওয়া
        stmt = select(DeviceSession).where(DeviceSession.user_id == user.id, DeviceSession.is_active == True)
        for s in db.scalars(stmt).all():
            s.is_active = False

        db.commit()
        return {"status": "password_reset", "message": "পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে! অনুগ্রহ করে নতুন করে লগইন করুন।"}
