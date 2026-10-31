from pydantic import BaseModel, EmailStr, Field

class EmailRequest(BaseModel):
    recipient_email: EmailStr = Field(..., description="Target recipient email address")
    subject: str = Field(..., min_length=3, max_length=150, description="Email subject line")
    user_name: str = Field(..., min_length=2, max_length=50, description="Recipient full name")
    message: str = Field(..., min_length=5, description="Main body message content")

class EmailResponse(BaseModel):
    status: str
    message: str
