from celery import Celery
from typing import Dict, List
from ..config import settings
from ..crawlers.google_maps import GoogleMapsCrawler
from ..crawlers.yelp import YelpCrawler
from ..ai.restaurant_labeler import RestaurantLabeler
from ..models.restaurant import Restaurant
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('crawler_tasks',
                   broker=settings.REDIS_URI,
                   backend=settings.REDIS_URI)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
db = mongo_client[settings.MONGODB_DB]
restaurants_collection = db.restaurants

@celery_app.task(name="crawl_location")
def crawl_location(location: Dict[str, float], radius_km: int = None):
    """Crawl restaurants in a specific location"""
    async def _crawl():
        restaurants = []
        
        # Crawl from Google Maps
        async with GoogleMapsCrawler() as google_crawler:
            try:
                google_restaurants = await google_crawler.process_location(location, radius_km)
                restaurants.extend(google_restaurants)
            except Exception as e:
                logger.error(f"Error crawling Google Maps: {str(e)}")

        # Crawl from Yelp
        async with YelpCrawler() as yelp_crawler:
            try:
                yelp_restaurants = await yelp_crawler.process_location(location, radius_km)
                restaurants.extend(yelp_restaurants)
            except Exception as e:
                logger.error(f"Error crawling Yelp: {str(e)}")

        return restaurants

    # Run the async crawl
    restaurants = asyncio.run(_crawl())
    
    # Queue restaurants for processing
    for restaurant in restaurants:
        process_restaurant.delay(restaurant.dict())

    return len(restaurants)

@celery_app.task(name="process_restaurant")
def process_restaurant(restaurant_data: Dict):
    """Process and label a single restaurant"""
    async def _process():
        try:
            # Convert dict back to Restaurant model
            restaurant = Restaurant(**restaurant_data)
            
            # Initialize labeler
            labeler = RestaurantLabeler()
            
            # Extract attributes
            attributes = await labeler.extract_attributes(restaurant)
            confidence_scores = labeler.get_confidence_scores(attributes)
            
            # Update restaurant with extracted attributes
            restaurant.attributes = attributes
            
            # Store in MongoDB
            await restaurants_collection.update_one(
                {"id": restaurant.id},
                {"$set": {
                    **restaurant.dict(),
                    "confidence_scores": confidence_scores,
                    "processed": True
                }},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing restaurant: {str(e)}")
            return False

    return asyncio.run(_process())

@celery_app.task(name="crawl_all_locations")
def crawl_all_locations():
    """Crawl all default locations"""
    for location in settings.DEFAULT_LOCATIONS:
        crawl_location.delay(location)

@celery_app.task(name="update_restaurants")
def update_restaurants():
    """Update existing restaurants"""
    async def _update():
        try:
            # Find restaurants that need updating
            cursor = restaurants_collection.find({
                "last_updated": {
                    "$lt": datetime.utcnow() - timedelta(days=7)  # Update weekly
                }
            })
            
            async for restaurant in cursor:
                process_restaurant.delay(restaurant)
                
        except Exception as e:
            logger.error(f"Error updating restaurants: {str(e)}")

    asyncio.run(_update()) 