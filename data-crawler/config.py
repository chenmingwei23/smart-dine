from pydantic import BaseSettings
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class CrawlerSettings(BaseSettings):
    # API Keys
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    YELP_API_KEY: str = os.getenv("YELP_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "smartdine")
    
    # Redis
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://localhost:6379")
    
    # AWS
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Crawler Settings
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    CONCURRENT_REQUESTS: int = 5
    
    # Location Settings
    DEFAULT_RADIUS_KM: int = 5
    DEFAULT_LOCATIONS: List[Dict[str, float]] = [
        {"lat": 40.7128, "lng": -74.0060},  # New York
        {"lat": 34.0522, "lng": -118.2437},  # Los Angeles
        # Add more default locations
    ]
    
    # Restaurant Attributes
    RESTAURANT_ATTRIBUTES: List[str] = [
        "cuisine_type",
        "price_level",
        "service_speed",
        "ambiance",
        "noise_level",
        "parking_availability",
        "dietary_options",
        "popular_dishes",
        "peak_hours",
        "wait_time",
    ]
    
    class Config:
        case_sensitive = True

settings = CrawlerSettings() 