import os
import secrets
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

logger = logging.getLogger("revivo.security")

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReVivo API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # DATABASE
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./revivo.db"
    )
    
    # AUTHENTICATION
    # Secure random secret fallback if not explicitly provided in development
    JWT_SECRET: str = os.getenv("JWT_SECRET", "revivo_dev_secret_key_9f38bc1a4e21a8d05e26b1c7f0d34a5b")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # REDIS / CACHE
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # PAYMENT ARCHITECTURE
    PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "sandbox")
    PAYMENT_SANDBOX_MODE: bool = os.getenv("PAYMENT_SANDBOX_MODE", "true").lower() in ("true", "1", "yes")
    PLATFORM_FEE_PERCENTAGE: float = 15.0 # 15% platform commission
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

if settings.ENVIRONMENT == "production" and (
    not settings.JWT_SECRET or "dev" in settings.JWT_SECRET or len(settings.JWT_SECRET) < 32
):
    raise ValueError("Production environment requires a strong, unique JWT_SECRET of at least 32 characters.")
