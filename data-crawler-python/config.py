from typing import Dict, Any

# Search area configuration
SEARCH_CONFIG = {
    "area": "San Francisco, CA",  # Area to search
    "radius_km": 5,  # Search radius in kilometers
    "max_restaurants": 100,  # Maximum number of restaurants to scrape
    "max_reviews_per_restaurant": 50,  # Maximum reviews to collect per restaurant
}

# MongoDB configuration
MONGODB_CONFIG = {
    "url": "mongodb://localhost:27017/",
    "db_name": "smartdine",
    "collection_restaurants": "restaurants",
    "collection_reviews": "reviews"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "scraper.log"
}

# Search filters
RESTAURANT_FILTERS = {
    "min_rating": 3.5,  # Minimum rating to include
    "cuisine_types": [],  # Empty list means all cuisines
    "price_levels": [],  # Empty list means all price levels (1-4)
} 