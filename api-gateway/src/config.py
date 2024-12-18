from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # API Gateway Settings
    API_GATEWAY_HOST: str = "0.0.0.0"
    API_GATEWAY_PORT: int = 8000
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    RESTAURANT_SERVICE_URL: str = "http://restaurant-service:8002"
    PREFERENCE_SERVICE_URL: str = "http://preference-service:8003"
    REVIEW_SERVICE_URL: str = "http://review-service:8004"
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React web app
        "http://localhost:19006",  # React Native web
        "capacitor://localhost",   # Mobile app
    ]
    
    # Rate Limiting
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60  # seconds
    
    # Redis (for rate limiting and caching)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 