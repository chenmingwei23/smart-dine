"""
Application settings and configuration.
"""

import os
from typing import Dict, List
from pathlib import Path
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get MongoDB URL from environment
mongodb_url = os.getenv('CRAWLER_MONGODB_URL', 'mongodb://localhost:27017/')
print(f"\nEnvironment variables:")
print(f"CRAWLER_MONGODB_URL: {mongodb_url}")
print(f"All env vars: {dict(os.environ)}\n")

class Settings(BaseSettings):
    """Crawler configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow'
    )
    
    # Search configuration
    area: str = Field(default="San Francisco, CA", env="CRAWLER_AREA")
    radius_km: int = Field(default=5, env="CRAWLER_RADIUS_KM")
    max_restaurants: int = Field(default=1, env="CRAWLER_MAX_RESTAURANTS")
    max_reviews_per_restaurant: int = Field(default=20, env="CRAWLER_MAX_REVIEWS_PER_RESTAURANT")
    
    # Restaurant filters
    min_rating: float = Field(default=4.0, env="CRAWLER_MIN_RATING")
    cuisine_types: List[str] = []
    price_levels: List[int] = []
    
    # MongoDB settings
    mongodb_url: str = "mongodb+srv://admin:admin@cluster0.h11zy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    mongodb_db: str = "smartdine"
    mongodb_collection_restaurants: str = "restaurants"
    mongodb_collection_reviews: str = "reviews"
    
    # Logging settings
    log_level: str = Field(default="INFO", env="CRAWLER_LOG_LEVEL")
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_file: str = "crawler.log"

# Create settings instance
settings = Settings()

# Debug output
print("\nLoaded settings:")
print(f"MongoDB URL: {settings.mongodb_url}")
print(f"MongoDB DB: {settings.mongodb_db}")
print(f"Area: {settings.area}")
print(f"Max restaurants: {settings.max_restaurants}")
print(f"Min rating: {settings.min_rating}\n") 