import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeOps AI - Enterprise Industrial Safety System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./safeops.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "safeops-ai-super-secret-industrial-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BLOCK_RISK_THRESHOLD: float = 65.0
    SUPERVISOR_APPROVAL_THRESHOLD: float = 40.0
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()
