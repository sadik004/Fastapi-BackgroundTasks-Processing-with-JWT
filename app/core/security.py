from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings  # ১ নম্বর ফাইল থেকে গোপন চাবি (SECRET_KEY) নিল

# ১. বিশ্বের সবচেয়ে শক্তিশালী Argon2 হ্যাশার চালু করা
password_hash = PasswordHash.recommended()

# ২. সাধারণ পাসওয়ার্ডকে Argon2 দিয়ে লক (Hash) করার ফাংশন
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# ৩. লগইনের সময় পাসওয়ার্ড সঠিক কি না তা মেলানোর ফাংশন
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# ৪. লগইন ও ওটিপি সফল হলে JWT Access Token তৈরির ফাংশন
def create_access_token(user_id: int, session_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),       # কার টোকেন (User ID)
        "session_id": session_id,  # কোন ডিভাইসের সেশন (কম্পিউটার নাকি ফোন ট্র্যাক করতে)
        "exp": expire              # টোকেনের মেয়াদ কবে শেষ হবে
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# ৫. টোকেন খুলে ভেতরের তথ্য পড়ার ফাংশন
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])