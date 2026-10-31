import sys
from pathlib import Path
from contextlib import asynccontextmanager

# ১. পাইথনকে মূল 'Sports' ফোল্ডারের পথ সবার আগে চিনিয়ে দেওয়া
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine, Base
import app.models.user  # টেবিল মেটাডাটা রেজিস্ট্রেশনের জন্য মডেল ইমপোর্ট
from app.api import emails, auth

# ২. আধুনিক Lifespan মেকানিজম: সার্ভার চালু হওয়ার সময় টেবিল তৈরি নিশ্চিত করা
@asynccontextmanager
async def lifespan(app: FastAPI):
    # স্টার্টআপ: sports_app.db-তে টেবিল না থাকলে অটোমেটিক তৈরি হবে
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# ৩. এপিআই রাউটারসমূহ সংযুক্ত করা
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication & Device Management"]
)

app.include_router(
    emails.router,
    prefix=f"{settings.API_V1_STR}/emails",
    tags=["Email Operations"]
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# ৪. Play বাটনে রান করার ব্লক
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
