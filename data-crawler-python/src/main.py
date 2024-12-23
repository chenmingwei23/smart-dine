"""
Main script for running the Google Maps crawler.
"""

import logging
import sys
from typing import Dict

from src.crawler.google_maps_crawler import GoogleMapsScraper
from src.database.mongodb import MongoDBClient
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def process_restaurant(scraper: GoogleMapsScraper, mongodb_client: MongoDBClient, url: str):
    """Process a single restaurant."""
    try:
        logger.info(f"Processing restaurant URL: {url}")
        
        # Get restaurant data
        result = scraper.get_account(url)
        if not result:
            logger.error(f"Failed to get data for URL: {url}")
            return
            
        restaurant_data = result.get('restaurant')
        reviews_data = result.get('reviews', [])
        
        if not restaurant_data:
            logger.error(f"No restaurant data found for URL: {url}")
            return
            
        logger.info(f"Saving restaurant: {restaurant_data.get('name')}")
        
        # Save restaurant data
        result = mongodb_client.upsert_restaurant(restaurant_data)
        if not result:
            logger.error(f"Failed to save restaurant data for URL: {url}")
            return
            
        # Save reviews if any
        if reviews_data:
            logger.info(f"Saving {len(reviews_data)} reviews")
            mongodb_client.upsert_reviews(restaurant_data['_id'], reviews_data)
        
    except Exception as e:
        logger.error(f"Error processing restaurant {url}: {str(e)}")

def main():
    """Main function to run the crawler."""
    try:
        # Initialize MongoDB client
        mongodb = MongoDBClient(
            mongodb_url=settings.MONGODB_URL,
            db_name=settings.MONGODB_DB,
            collection_restaurants=settings.MONGODB_COLLECTION_RESTAURANTS,
            collection_reviews=settings.MONGODB_COLLECTION_REVIEWS
        )
        
        # Create indexes
        mongodb.create_indexes()
        
        # Initialize scraper
        with GoogleMapsScraper(debug=True) as scraper:
            # Example restaurant URLs
            urls = [
                "https://www.google.com/maps/place/Rich+Table/data=!4m7!3m6!1s0x80858093eabc4f2d:0x68f428012b5db354!8m2!3d37.7743021!4d-122.4212768!16s%2Fg%2F1q5bmz5wy!19sChIJLfK8rJOAhYARVLNbKwGIb2g?authuser=0&hl=en&rclk=1",
                "https://www.google.com/maps/place/Delancey+Street+Restaurant/data=!4m7!3m6!1s0x808580770df6174d:0x8be3ee157d693ab2!8m2!3d37.7843599!4d-122.3884342!16s%2Fm%2F04fjq0y!19sChIJTRf2DXeAhYARsjppfRXu44s?authuser=0&hl=en&rclk=1"
            ]
            
            # Process each restaurant
            for url in urls:
                process_restaurant(scraper, mongodb, url)
                
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 