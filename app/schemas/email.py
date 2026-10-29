from pydantic import BaseModel, EmailStr, Field

class EmailRequest(BaseModel):
    recipient_email: EmailStr = Field(..., description="প্রাপকের সঠিক ইমেইল অ্যাড্রেস")
    subject: str = Field(..., min_length=3, max_length=150, description="ইমেইলের বিষয়")
    user_name: str = Field(..., min_length=2, max_length=50, description="গ্রাহকের নাম")
    message: str = Field(..., min_length=5, description="ইমেইলের মূল বক্তব্য")  # <-- নতুন যোগ হলো

class EmailResponse(BaseModel):
    status: str
    message: str