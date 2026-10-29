from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# মূল Sports ফোল্ডারে থাকা .env ফাইলের সঠিক পথ বের করা
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Email Service"
    API_V1_STR: str = "/api/v1"
    
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@company.com"

    # সরাসরি .env ফাইলের আসল পথ দেওয়া হলো
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()