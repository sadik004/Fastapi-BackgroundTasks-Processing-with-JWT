from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Auth & Email Service"
    API_V1_STR: str = "/api/v1"
    
    # ১. ডাটাবেজ কানেকশন (প্রজেক্ট ফোল্ডারেই sports_app.db নামে ফাইল তৈরি হবে)
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'sports_app.db'}"
    
    # ২. JWT টোকেন ও ওটিপি সিকিউরিটি সেটিংস
    JWT_SECRET_KEY: str = "super-secret-enterprise-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OTP_EXPIRE_MINUTES: int = 5

    # ৩. SMTP ইমেইল সেটিংস
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@company.com"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()