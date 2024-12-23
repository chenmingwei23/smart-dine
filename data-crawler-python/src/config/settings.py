"""
Application settings and configuration.
"""

from typing import Dict, List
from pydantic import BaseSettings, Field

class CrawlerSettings(BaseSettings):
    """Crawler configuration settings."""
    
    # Search configuration
    area: str = "San Francisco, CA"
    radius_km: int = 5
    max_restaurants: int = 100
    max_reviews_per_restaurant: int = 50
    
    # Restaurant filters
    min_rating: float = 3.5
    cuisine_types: List[str] = []
    price_levels: List[int] = []
    
    # MongoDB settings
    mongodb_url: str = "mongodb://localhost:27017/"
    mongodb_db: str = "smartdine"
    mongodb_collection_restaurants: str = "restaurants"
    mongodb_collection_reviews: str = "reviews"
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_file: str = "crawler.log"
    
    class Config:
        env_prefix = "CRAWLER_"  # Environment variables prefix
        case_sensitive = False

# Create settings instance
settings = CrawlerSettings() 