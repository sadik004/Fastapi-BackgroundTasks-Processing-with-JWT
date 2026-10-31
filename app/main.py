import sys
from pathlib import Path
from contextlib import asynccontextmanager

# 1. Ensure project root directory is on Python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine, Base
import app.models.user  # Register entity metadata with Base
from app.api import emails, auth

# 2. Modern ASGI Lifespan: Bootstrap database schema tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables in sports_app.db if they do not exist
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# 3. Mount API Routers
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

# 4. Entrypoint for standalone IDE execution
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
