from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from pydantic import validator
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartDine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = "smartdine"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]  # Update in production
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 