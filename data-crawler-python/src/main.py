"""
Main entry point for the restaurant crawler.
"""

import logging
from pathlib import Path
from urllib.parse import quote_plus
from src.crawler.google_maps_crawler import GoogleMapsScraper
from src.database.mongodb import MongoDBClient
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format=settings.log_format,
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_restaurant(scraper: GoogleMapsScraper, mongodb_client: MongoDBClient, url: str) -> None:
    """Process a single restaurant URL."""
    try:
        # Get restaurant data and reviews
        result = scraper.get_account(url)
        
        # Extract restaurant data and reviews from result
        restaurant_data = result.get('restaurant', {})
        reviews = result.get('reviews', [])
        
        # Save restaurant data
        if restaurant_data and restaurant_data.get('name'):
            logger.info(f"Saving restaurant: {restaurant_data.get('name')}")
            # Upsert restaurant first to ensure we have an ID
            result = mongodb_client.upsert_restaurant(restaurant_data)
            
            # Save reviews if available
            if reviews:
                logger.info(f"Saving {len(reviews)} reviews")
                # Use the restaurant's ID for the reviews
                restaurant_id = restaurant_data.get('_id')
                if restaurant_id:
                    mongodb_client.upsert_reviews(restaurant_id, reviews)
                else:
                    logger.error("Cannot save reviews: missing restaurant ID")
        else:
            logger.warning(f"No valid restaurant data found for URL: {url}")
            
    except Exception as e:
        logger.error(f"Error processing restaurant {url}: {str(e)}")
        raise

def main():
    """Main execution function."""
    try:
        # Initialize MongoDB client
        mongodb = MongoDBClient(
            mongodb_url=settings.mongodb_url,
            db_name=settings.mongodb_db,
            collection_restaurants=settings.mongodb_collection_restaurants,
            collection_reviews=settings.mongodb_collection_reviews
        )
        
        # Create indexes
        mongodb.create_indexes()
        
        # Initialize scraper
        with GoogleMapsScraper(debug=False) as scraper:
            # Search for restaurants in the area
            search_url = f"https://www.google.com/maps/search/restaurants+in+{quote_plus(settings.area)}"
            logger.info(f"Searching restaurants in {settings.area}")
            
            # Get list of restaurant URLs
            restaurant_urls = scraper.search_restaurants(search_url, max_results=settings.max_restaurants)
            logger.info(f"Found {len(restaurant_urls)} restaurants")
            
            # Process each restaurant
            for i, url in enumerate(restaurant_urls, 1):
                try:
                    logger.info(f"Processing restaurant {i}/{len(restaurant_urls)}: {url}")
                    process_restaurant(scraper, mongodb, url)
                    
                except Exception as e:
                    logger.error(f"Error processing restaurant {url}: {str(e)}")
                    continue
                
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise
    finally:
        mongodb.close()

if __name__ == "__main__":
    main() 