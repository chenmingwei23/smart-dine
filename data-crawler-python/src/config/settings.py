"""
Application settings and configuration.
"""

import os
from typing import Dict, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CrawlerSettings(BaseSettings):
    """Crawler configuration settings."""
    
    # Search configuration
    area: str = Field(default="San Francisco, CA", env="CRAWLER_AREA")
    radius_km: int = Field(default=5, env="CRAWLER_RADIUS_KM")
    max_restaurants: int = Field(default=100, env="CRAWLER_MAX_RESTAURANTS")
    max_reviews_per_restaurant: int = Field(default=50, env="CRAWLER_MAX_REVIEWS_PER_RESTAURANT")
    
    # Restaurant filters
    min_rating: float = Field(default=3.5, env="CRAWLER_MIN_RATING")
    cuisine_types: List[str] = []
    price_levels: List[int] = []
    
    # MongoDB settings
    mongodb_url: str = Field(
        default="mongodb://localhost:27017/",
        env="CRAWLER_MONGODB_URL",
        description="MongoDB connection string. For Atlas, use: mongodb+srv://username:password@cluster-url/database"
    )
    mongodb_db: str = Field(default="smartdine", env="CRAWLER_MONGODB_DB")
    mongodb_collection_restaurants: str = Field(
        default="restaurants",
        env="CRAWLER_MONGODB_COLLECTION_RESTAURANTS"
    )
    mongodb_collection_reviews: str = Field(
        default="reviews",
        env="CRAWLER_MONGODB_COLLECTION_REVIEWS"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", env="CRAWLER_LOG_LEVEL")
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_file: str = "crawler.log"
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

# Create settings instance
settings = CrawlerSettings() 