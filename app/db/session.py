from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# 1. Thread check configuration for SQLite / PostgreSQL
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# 2. Initialize SQLAlchemy database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# 3. Create scoped session factory for persistence operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative base class for all database entities (SQLAlchemy 2.0 Standard)
class Base(DeclarativeBase):
    pass

# 5. Dependency generator managing transactional database session lifecycle
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
