from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, DeviceSession
from app.schemas.auth import (
    SignupRequest, VerifySignupOTPRequest,
    LoginRequest, VerifyLoginOTPRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    MessageResponse, TokenResponse
)
from app.services.auth_service import AuthService

router = APIRouter()
security_scheme = HTTPBearer()

# ================= 1. Signup & OTP Verification Endpoints =================
@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def signup_endpoint(
    payload: SignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return AuthService.signup(db, payload, background_tasks)

@router.post("/verify-signup", response_model=MessageResponse)
def verify_signup_endpoint(
    payload: VerifySignupOTPRequest,
    db: Session = Depends(get_db)
):
    return AuthService.verify_signup(db, payload)


# ================= 2. Login, 2FA OTP & Device Session Endpoints =================
@router.post("/login", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def login_endpoint(
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return AuthService.login(db, payload, background_tasks)

@router.post("/verify-login", response_model=TokenResponse)
def verify_login_endpoint(
    payload: VerifyLoginOTPRequest,
    db: Session = Depends(get_db)
):
    return AuthService.verify_login(db, payload)


# ================= 3. Forgot & Reset Password Endpoints =================
@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def forgot_password_endpoint(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return AuthService.forgot_password(db, payload, background_tasks)

@router.post("/reset-password", response_model=MessageResponse)
def reset_password_endpoint(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return AuthService.reset_password(db, payload)


# ================= 4. Authenticated Profile & Session Health Endpoint =================
@router.get("/me", summary="Validate active token and device session")
def get_my_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    try:
        data = decode_access_token(credentials.credentials)
        user_id = int(data["sub"])
        session_id = data["session_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token or session expired.")

    # Validate that this specific device session is still active (is_active=True)
    session_record = db.scalar(
        select(DeviceSession).where(
            DeviceSession.id == session_id,
            DeviceSession.is_active == True
        )
    )
    if not session_record:
        raise HTTPException(
            status_code=401,
            detail="Session revoked: You have been logged out because another device logged in."
        )

    user = db.scalar(select(User).where(User.id == user_id))
    return {
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "current_device": f"{session_record.device_type} ({session_record.device_name})"
    }
