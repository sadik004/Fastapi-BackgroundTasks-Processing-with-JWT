from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings  # ১ নম্বর ফাইল থেকে ডাটাবেজের ঠিকানা নিল

# ১. SQLite হলে মাল্টি-থ্রেড চেক বন্ধ রাখা, আর PostgreSQL হলে খালি রাখা
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# ২. ডাটাবেজের মূল ইঞ্জিন তৈরি
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# ৩. ডাটাবেজে কথা বলার জন্য সেশন ফ্যাক্টরি তৈরি
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ৪. সব টেবিল বানানোর মূল ভিত্তি (SQLAlchemy 2.0 আধুনিক স্ট্যান্ডার্ড)
class Base(DeclarativeBase):
    pass

# ৫. প্রতি রিকোয়েস্টে ডাটাবেজ কানেকশন খুলে কাজ শেষে অটোমেটিক বন্ধ করার ফাংশন
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()