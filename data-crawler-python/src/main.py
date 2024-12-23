"""
Main entry point for the restaurant crawler application.
"""

import logging
from typing import List, Optional
import uuid

from .config.settings import settings
from .crawler.google_maps_crawler import GoogleMapsScraper
from .database.mongodb import MongoDBClient
from .models.restaurant import Restaurant, Review, Location, OpeningHours, RestaurantAttributes

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format=settings.log_format,
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_restaurant_data(place_data: dict, url: str) -> Restaurant:
    """Parse raw place data into Restaurant model."""
    # Parse location
    location = Location(
        lat=place_data.get('coordinates', {}).get('lat', 0.0),
        lng=place_data.get('coordinates', {}).get('lng', 0.0),
        address=place_data.get('address', ''),
        city='',  # Will be parsed from address
        state='',
        country='',
        postal_code=''
    )
    
    # Parse opening hours
    opening_hours = []
    hours_data = place_data.get('opening_hours', {})
    for day, hours in hours_data.items():
        if isinstance(hours, dict):
            opening_hours.append(OpeningHours(
                day=int(day),
                open_time=hours.get('open', '09:00'),
                close_time=hours.get('close', '17:00')
            ))
    
    # Create restaurant object
    return Restaurant(
        id=str(uuid.uuid4()),
        name=place_data.get("name", "Unknown"),
        location=location,
        phone=place_data.get("phone"),
        website=place_data.get("website"),
        opening_hours=opening_hours,
        overall_rating=float(place_data.get("overall_rating", 0.0)),
        total_reviews=int(place_data.get("total_reviews", 0)),
        attributes=RestaurantAttributes(
            cuisine_type=place_data.get('cuisine_type', []),
            price_level=place_data.get('price_level')
        ),
        photos=place_data.get("photos", []),
        url=url,
        raw_data=place_data
    )

def should_include_restaurant(place_data: dict) -> bool:
    """Check if restaurant meets the filter criteria."""
    if settings.min_rating:
        rating = float(place_data.get("overall_rating", 0))
        if rating < settings.min_rating:
            return False
            
    if settings.cuisine_types:
        restaurant_cuisines = place_data.get("cuisine_type", [])
        if not any(cuisine in settings.cuisine_types for cuisine in restaurant_cuisines):
            return False
            
    if settings.price_levels:
        price_level = place_data.get("price_level")
        if price_level not in settings.price_levels:
            return False
            
    return True

def main():
    """Main execution function."""
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting crawler for area: {settings.area}")
    
    # Initialize database client
    db = MongoDBClient(
        mongo_url=settings.mongodb_url,
        db_name=settings.mongodb_db
    )
    
    try:
        with GoogleMapsScraper(debug=False) as scraper:
            # Search for restaurants in the area
            search_url = f"https://www.google.com/maps/search/restaurants+in+{settings.area.replace(' ', '+')}/"
            logger.info(f"Searching restaurants in area: {settings.area}")
            
            restaurant_urls = scraper.search_restaurants(
                search_url, 
                max_results=settings.max_restaurants
            )
            
            logger.info(f"Found {len(restaurant_urls)} restaurants")
            
            # Scrape each restaurant
            for i, url in enumerate(restaurant_urls, 1):
                logger.info(f"Processing restaurant {i}/{len(restaurant_urls)}: {url}")
                
                try:
                    # Get restaurant data
                    place_data = scraper.get_account(url)
                    if not place_data or not should_include_restaurant(place_data):
                        continue

                    # Parse restaurant data
                    restaurant = parse_restaurant_data(place_data, url)
                    
                    # Get reviews
                    if scraper.sort_by(url, 1) == 0:  # 1 for newest reviews
                        n = 0
                        while n < settings.max_reviews_per_restaurant:
                            reviews = scraper.get_reviews(n)
                            if not reviews:
                                break

                            for r in reviews:
                                review = Review(
                                    id_review=r["id_review"],
                                    caption=r.get("caption"),
                                    relative_date=r["relative_date"],
                                    timestamp=r["retrieval_date"],
                                    rating=float(r["rating"]),
                                    username=r.get("username"),
                                    n_review_user=int(r.get("n_review_user", 0)),
                                    n_photo_user=int(r.get("n_photo_user", 0)),
                                    url_user=r.get("url_user")
                                )
                                restaurant.reviews.append(review)
                            n += len(reviews)

                    # Store in database
                    restaurant_id = db.upsert_restaurant(restaurant)
                    logger.info(f"Stored restaurant: {restaurant.name} with {len(restaurant.reviews)} reviews")
                    
                except Exception as e:
                    logger.error(f"Error processing restaurant {url}: {str(e)}", exc_info=True)
                    continue
                
    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}", exc_info=True)
    finally:
        db.close()
        logger.info("Crawling completed")

if __name__ == "__main__":
    main() 