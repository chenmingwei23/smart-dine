# -*- coding: utf-8 -*-
import logging
from typing import List, Optional
from googlemaps import GoogleMapsScraper
from datetime import datetime
import uuid
from models.restaurant import Restaurant, Review, Location, OpeningHours, RestaurantAttributes
from dao.restaurant_dao import RestaurantDAO
from config import SEARCH_CONFIG, MONGODB_CONFIG, LOGGING_CONFIG, RESTAURANT_FILTERS

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG["file"]),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_address(address_str: str) -> Location:
    """Parse address string into Location object with best effort"""
    parts = address_str.split(',')
    return Location(
        lat=0.0,  # Will be updated with actual coordinates
        lng=0.0,
        address=parts[0].strip() if parts else "",
        city=parts[1].strip() if len(parts) > 1 else "",
        state=parts[2].strip() if len(parts) > 2 else "",
        country=parts[-1].strip() if len(parts) > 3 else "",
        postal_code=""
    )

def parse_opening_hours(hours_data: dict) -> List[OpeningHours]:
    """Parse opening hours data into OpeningHours objects"""
    hours_list = []
    if not hours_data:
        return hours_list
        
    for day in range(7):
        if str(day) in hours_data:
            hours = hours_data[str(day)]
            hours_list.append(OpeningHours(
                day=day,
                open_time=hours.get('open', '09:00'),
                close_time=hours.get('close', '17:00'),
                is_overnight=False
            ))
    return hours_list

def parse_attributes(place_data: dict) -> RestaurantAttributes:
    """Parse place data into RestaurantAttributes"""
    return RestaurantAttributes(
        cuisine_type=place_data.get('cuisine_type', []),
        price_level=place_data.get('price_level'),
        service_speed=None,
        ambiance=None,
        noise_level=None,
        parking_availability=None,
        dietary_options=None,
        popular_dishes=None,
        peak_hours=None,
        wait_time=None
    )

def should_include_restaurant(place_data: dict) -> bool:
    """Check if restaurant meets the filter criteria"""
    if RESTAURANT_FILTERS["min_rating"]:
        rating = float(place_data.get("overall_rating", 0))
        if rating < RESTAURANT_FILTERS["min_rating"]:
            return False
            
    if RESTAURANT_FILTERS["cuisine_types"]:
        restaurant_cuisines = place_data.get("cuisine_type", [])
        if not any(cuisine in RESTAURANT_FILTERS["cuisine_types"] for cuisine in restaurant_cuisines):
            return False
            
    if RESTAURANT_FILTERS["price_levels"]:
        price_level = place_data.get("price_level")
        if price_level not in RESTAURANT_FILTERS["price_levels"]:
            return False
            
    return True

def scrape_restaurant(url: str, dao: RestaurantDAO, logger: logging.Logger) -> Optional[str]:
    """Scrape a single restaurant and return its ID if successful"""
    with GoogleMapsScraper(debug=False) as scraper:
        # Get restaurant info
        place_data = scraper.get_account(url)
        if not place_data:
            logger.error(f"Failed to get data for {url}")
            return None

        if not should_include_restaurant(place_data):
            logger.info(f"Skipping restaurant {place_data.get('name')} - doesn't meet filter criteria")
            return None

        # Parse location from address
        location = parse_address(place_data.get('address', ''))
        if place_data.get('coordinates'):
            location.lat = place_data['coordinates']['lat']
            location.lng = place_data['coordinates']['lng']
        
        # Parse opening hours and attributes
        opening_hours = parse_opening_hours(place_data.get('opening_hours', {}))
        attributes = parse_attributes(place_data)

        # Create restaurant object
        restaurant = Restaurant(
            id=str(uuid.uuid4()),
            name=place_data.get("name", "Unknown"),
            location=location,
            phone=place_data.get("phone"),
            website=place_data.get("website"),
            opening_hours=opening_hours,
            overall_rating=float(place_data.get("overall_rating", 0.0)),
            total_reviews=int(place_data.get("total_reviews", 0)),
            attributes=attributes,
            photos=place_data.get("photos", []),
            url=url,
            raw_data=place_data
        )

        # Get reviews
        error = scraper.sort_by(url, 1)  # 1 for newest reviews
        if error == 0:
            n = 0
            while n < SEARCH_CONFIG["max_reviews_per_restaurant"]:
                logger.debug(f'Fetching reviews {n}-{n+10}')
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
                        url_user=r.get("url_user"),
                        likes=None
                    )
                    restaurant.reviews.append(review)
                n += len(reviews)

        # Store in MongoDB
        restaurant_id = dao.upsert_restaurant(restaurant)
        logger.info(f"Stored restaurant: {restaurant.name} with {len(restaurant.reviews)} reviews")
        return restaurant_id

def main():
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting scraper for area: {SEARCH_CONFIG['area']}")
    
    # Initialize DAO
    dao = RestaurantDAO(
        mongo_url=MONGODB_CONFIG["url"],
        db_name=MONGODB_CONFIG["db_name"]
    )
    
    try:
        with GoogleMapsScraper(debug=False) as scraper:
            # Search for restaurants in the area
            search_url = f"https://www.google.com/maps/search/restaurants+in+{SEARCH_CONFIG['area'].replace(' ', '+')}/"
            logger.info(f"Searching restaurants in area: {SEARCH_CONFIG['area']}")
            
            restaurant_urls = scraper.search_restaurants(
                search_url, 
                max_results=SEARCH_CONFIG["max_restaurants"]
            )
            
            logger.info(f"Found {len(restaurant_urls)} restaurants")
            
            # Scrape each restaurant
            for i, url in enumerate(restaurant_urls, 1):
                logger.info(f"Processing restaurant {i}/{len(restaurant_urls)}: {url}")
                restaurant_id = scrape_restaurant(url, dao, logger)
                if restaurant_id:
                    logger.info(f"Successfully scraped restaurant {i} (ID: {restaurant_id})")
                
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
    finally:
        dao.close()
        logger.info("Scraping completed")

if __name__ == '__main__':
    main()
