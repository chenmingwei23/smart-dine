"""
Configuration settings for the crawler.
"""

import os
import logging

class Settings:
    """Settings class for the crawler."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # MongoDB settings
        self.MONGODB_URL = os.getenv('CRAWLER_MONGODB_URL', 'mongodb+srv://admin:admin@cluster0.h11zy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        self.MONGODB_DB = os.getenv('CRAWLER_MONGODB_DB', 'smartdine')
        self.MONGODB_COLLECTION_RESTAURANTS = os.getenv('CRAWLER_MONGODB_COLLECTION_RESTAURANTS', 'restaurants')
        self.MONGODB_COLLECTION_REVIEWS = os.getenv('CRAWLER_MONGODB_COLLECTION_REVIEWS', 'reviews')
        
        # Crawler settings
        self.area = os.getenv('CRAWLER_AREA', 'San Francisco, CA')
        self.radius_km = float(os.getenv('CRAWLER_RADIUS_KM', '5'))
        self.max_restaurants = int(os.getenv('CRAWLER_MAX_RESTAURANTS', '1'))
        self.max_reviews_per_restaurant = int(os.getenv('CRAWLER_MAX_REVIEWS_PER_RESTAURANT', '20'))
        self.min_rating = float(os.getenv('CRAWLER_MIN_RATING', '4.0'))
        
        # Logging settings
        self.log_level = os.getenv('CRAWLER_LOG_LEVEL', 'INFO')
        self.log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Print loaded settings
        print("\nEnvironment variables:")
        print(f"CRAWLER_MONGODB_URL: {self.MONGODB_URL}")
        print(f"All env vars: {os.environ}")
        print("\n\nLoaded settings:")
        print(f"MongoDB URL: {self.MONGODB_URL}")
        print(f"MongoDB DB: {self.MONGODB_DB}")
        print(f"Area: {self.area}")
        print(f"Max restaurants: {self.max_restaurants}")
        print(f"Min rating: {self.min_rating}")

settings = Settings() 