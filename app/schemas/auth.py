from typing import Literal
from pydantic import BaseModel, EmailStr, Field

# ================= ১. সাইনআপ (Signup with OTP) =================
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="ইউজারের পূর্ণ নাম")
    email: EmailStr = Field(..., description="ইউজারের ইমেইল")
    address: str = Field(..., min_length=3, max_length=255, description="ইউজারের ঠিকানা")
    password: str = Field(..., min_length=6, description="পাসওয়ার্ড (কমপক্ষে ৬ অক্ষর)")

class VerifySignupOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="ইমেইলে যাওয়া ৬ ডিজিটের ওটিপি")


# ================= ২. লগইন ও ডিভাইস লিমিট (Login with OTP) =================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyLoginOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    # শুধুমাত্র "computer" অথবা "phone" গ্রহণ করবে (Swagger-এ ড্রপডাউন তৈরি হবে)
    device_type: Literal["computer", "phone"] = Field(..., description="ডিভাইসের ধরন: computer নাকি phone")
    device_name: str = Field(default="My Device", description="ডিভাইসের নাম (যেমন: Windows PC, iPhone)")


# ================= ৩. ফরগট পাসওয়ার্ড (Forgot Password with OTP) =================
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, description="নতুন পাসওয়ার্ড")


# ================= ৪. সার্ভারের উত্তর (Responses) =================
class MessageResponse(BaseModel):
    status: str
    message: str
    dev_otp: str | None = None  # ডেভেলপমেন্ট ও টেস্টিং সুবিধার জন্য সরাসরি ওটিপি রিটার্ন

class TokenResponse(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str = "bearer"
    device_info: str
