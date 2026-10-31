from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base  # ২ নম্বর ফাইল থেকে Base ধার নিল

# ১. ইউজারের মূল তথ্য রাখার টেবিল (users)
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

# ২. ৩টি কাজের (Signup, Login, Forgot) ওটিপি রাখার টেবিল (otp_codes)
class OTPCode(Base):
    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)  # "signup", "login", বা "forgot"
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

# ৩. ২টি কম্পিউটার ও ১টি ফোন ট্র্যাক করার টেবিল (device_sessions)
class DeviceSession(Base):
    __tablename__ = "device_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "computer" অথবা "phone"
    device_name: Mapped[str] = mapped_column(String(100), default="Unknown Device")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )