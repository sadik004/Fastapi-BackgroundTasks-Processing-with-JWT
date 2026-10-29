import sys
from pathlib import Path

# ১. পাইথনকে মূল 'Sports' ফোল্ডারের পথ চিনিয়ে দেওয়া
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# ২. এখন আর 'app' খুঁজে পেতে কোনো সমস্যা হবে না
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.api import emails

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs"
)

app.include_router(
    emails.router,
    prefix=f"{settings.API_V1_STR}/emails",
    tags=["Email Operations"]
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# ৩. Play বাটনে রান করার ব্লক
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)