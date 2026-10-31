from typing import Literal
from pydantic import BaseModel, EmailStr, Field

# ================= 1. Signup Request DTOs =================
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Valid user email address")
    address: str = Field(..., min_length=3, max_length=255, description="Physical address")
    password: str = Field(..., min_length=6, description="Plaintext password (min 6 characters)")

class VerifySignupOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification OTP code")


# ================= 2. Login & Device Session DTOs =================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyLoginOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification OTP code")
    device_type: Literal["computer", "phone"] = Field(..., description="Device classification: 'computer' or 'phone'")
    device_name: str = Field(default="My Device", description="Descriptive device name (e.g., Windows PC, iPhone)")


# ================= 3. Password Reset DTOs =================
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification OTP code")
    new_password: str = Field(..., min_length=6, description="New plaintext password (min 6 characters)")


# ================= 4. Standard Response DTOs =================
class MessageResponse(BaseModel):
    status: str
    message: str
    dev_otp: str | None = None  # Included for development and automated verification testing

class TokenResponse(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str = "bearer"
    device_info: str
