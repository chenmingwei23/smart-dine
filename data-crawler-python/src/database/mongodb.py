"""
MongoDB database operations.
Handles all database interactions for storing and retrieving restaurant data.
"""

from typing import List, Optional
import ssl
import logging
from urllib.parse import quote_plus
import re

from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from ..models.restaurant import Restaurant, Review
from ..config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for restaurant data storage."""
    
    def __init__(
        self,
        mongodb_url: str,
        db_name: str,
        collection_restaurants: str,
        collection_reviews: str
    ):
        """Initialize MongoDB client with connection details."""
        logger.info(f"Initializing MongoDB client with URL: {mongodb_url}")
        try:
            self.client = MongoClient(mongodb_url)
            self.db = self.client[db_name]
            self.restaurants = self.db[collection_restaurants]
            self.reviews = self.db[collection_reviews]
            logger.info("MongoDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            raise
    
    def create_indexes(self):
        """Create indexes for restaurants and reviews collections."""
        try:
            logger.info("Creating indexes for restaurants collection")
            
            # Drop existing indexes except _id
            logger.info("Dropping existing indexes")
            for index in self.restaurants.list_indexes():
                if index['name'] != '_id_':
                    self.restaurants.drop_index(index['name'])
            for index in self.reviews.list_indexes():
                if index['name'] != '_id_':
                    self.reviews.drop_index(index['name'])
            
            # Create new indexes
            logger.info("Creating new indexes")
            self.restaurants.create_index([("name", ASCENDING)])
            self.restaurants.create_index([("url", ASCENDING)])
            self.restaurants.create_index([("overall_rating", DESCENDING)])
            self.restaurants.create_index([("attributes.cuisine_type", ASCENDING)])
            self.restaurants.create_index([("attributes.price_level", ASCENDING)])
            
            # Create 2dsphere index only if coordinates are present
            self.restaurants.create_index([("location.coordinates", "2dsphere")])
            
            logger.info("Creating indexes for reviews collection")
            self.reviews.create_index([("restaurant_id", ASCENDING)])
            self.reviews.create_index([("rating", DESCENDING)])
            self.reviews.create_index([("date", DESCENDING)])
            
            logger.info("All indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    def upsert_restaurant(self, restaurant_data: dict):
        """Upsert a restaurant document."""
        try:
            if not restaurant_data:
                logger.error("No restaurant data provided")
                return None
                
            name = restaurant_data.get('name')
            if not name:
                logger.error("Restaurant data missing name field")
                return None
                
            logger.info(f"Upserting restaurant: {name}")
            
            # Create a copy of the data for update
            update_data = restaurant_data.copy()
            logger.debug(f"Created copy of update data: {update_data}")
            
            # Get the _id and url for query
            restaurant_id = update_data.pop('_id', None)
            restaurant_url = update_data.get('url')
            logger.info(f"Extracted ID: {restaurant_id}, URL: {restaurant_url}")
            
            if not restaurant_id:
                # If no _id, generate one from name
                restaurant_id = self.__generate_restaurant_id(name)
                logger.info(f"Generated new ID from name: {restaurant_id}")
            
            # Remove _id from update data
            if '_id' in update_data:
                del update_data['_id']
            
            # Clean up location data for GeoJSON
            if 'location' in update_data:
                location = update_data['location']
                # Only include coordinates if they exist and are valid
                if not location.get('coordinates') or len(location['coordinates']) != 2:
                    # Remove coordinates if they're not valid GeoJSON
                    if 'coordinates' in location:
                        del location['coordinates']
                    if 'type' in location:
                        del location['type']
            
            # First try to find by URL (since it's unique)
            existing = None
            if restaurant_url:
                logger.info(f"Searching for existing restaurant by URL: {restaurant_url}")
                existing = self.restaurants.find_one({"url": restaurant_url})
                if existing:
                    logger.info(f"Found existing restaurant: {existing.get('name')} with ID: {existing.get('_id')}")
            
            if existing:
                # If found by URL, use its _id
                query = {"_id": existing["_id"]}
                # Merge existing data with update data
                update_data = {**existing, **update_data}
                # Remove _id from update data again
                if '_id' in update_data:
                    del update_data['_id']
                logger.info(f"Using existing restaurant ID for update: {existing['_id']}")
            else:
                # Otherwise use our generated/provided _id
                query = {"_id": restaurant_id}
                logger.info(f"Using new/provided ID for update: {restaurant_id}")
            
            logger.debug(f"Final update query: {query}")
            logger.debug(f"Final update data: {update_data}")
            
            result = self.restaurants.update_one(
                query,
                {"$set": update_data},
                upsert=True
            )
            logger.info(f"Restaurant upsert result - upserted_id: {result.upserted_id}, modified_count: {result.modified_count}, matched_count: {result.matched_count}")
            return result
        except Exception as e:
            logger.error(f"Failed to upsert restaurant: {str(e)}", exc_info=True)
            raise
            
    def __generate_restaurant_id(self, name: str) -> str:
        """Generate a consistent restaurant ID from name."""
        # Clean the name: lowercase, remove special chars, replace spaces with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower()).strip()
        clean_name = re.sub(r'\s+', '_', clean_name)
        return clean_name
    
    def upsert_reviews(self, restaurant_id: str, reviews: List[dict]):
        """Upsert multiple review documents."""
        logger.info(f"Upserting {len(reviews)} reviews for restaurant {restaurant_id}")
        try:
            # Filter out reviews without valid IDs
            valid_reviews = [
                review for review in reviews 
                if review.get("_id") and review.get("text")  # Ensure we have both ID and content
            ]
            
            if not valid_reviews:
                logger.warning("No valid reviews to upsert")
                return None
                
            operations = []
            for review in valid_reviews:
                # Create a copy of the review data
                review_data = review.copy()
                
                # Set id_review to _id to satisfy the unique constraint
                review_data['id_review'] = review_data['_id']
                
                operations.append(
                    UpdateOne(
                        {"_id": review_data["_id"]},
                        {"$set": {**review_data, "restaurant_id": restaurant_id}},
                        upsert=True
                    )
                )
            
            if operations:
                result = self.reviews.bulk_write(operations)
                logger.info(f"Reviews upserted successfully: {result.upserted_count} inserted, {result.modified_count} modified")
                return result
            return None
            
        except Exception as e:
            logger.error(f"Failed to upsert reviews: {str(e)}")
            raise
    
    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        """Get a restaurant by ID."""
        try:
            logger.info(f"Retrieving restaurant with ID: {restaurant_id}")
            
            restaurant_dict = self.restaurants.find_one({"_id": restaurant_id})
            if not restaurant_dict:
                logger.warning(f"Restaurant not found with ID: {restaurant_id}")
                return None
                
            logger.info(f"Found restaurant {restaurant_dict.get('name')}")
            return Restaurant.parse_obj(restaurant_dict)
            
        except Exception as e:
            logger.error(f"Error retrieving restaurant {restaurant_id}: {str(e)}")
            raise
    
    def get_restaurant_reviews(self, restaurant_id: str, skip: int = 0, limit: int = 20) -> List[Review]:
        """Get reviews for a restaurant with pagination."""
        try:
            reviews = list(self.reviews.find(
                {"restaurant_id": restaurant_id}
            ).skip(skip).limit(limit))
            return [Review.parse_obj(r) for r in reviews]
        except Exception as e:
            logger.error(f"Error retrieving reviews for restaurant {restaurant_id}: {str(e)}")
            raise
    
    def get_restaurants(self, skip: int = 0, limit: int = 20) -> List[Restaurant]:
        """Get a list of restaurants with pagination."""
        try:
            restaurants = list(self.restaurants.find().skip(skip).limit(limit))
            return [Restaurant.parse_obj(r) for r in restaurants]
        except Exception as e:
            logger.error(f"Error retrieving restaurants: {str(e)}")
            raise
    
    def get_restaurant_by_url(self, url: str) -> Optional[Restaurant]:
        """Get a restaurant by its Google Maps URL."""
        try:
            restaurant_dict = self.restaurants.find_one({"url": url})
            if not restaurant_dict:
                return None
            return Restaurant.parse_obj(restaurant_dict)
        except Exception as e:
            logger.error(f"Error retrieving restaurant by URL {url}: {str(e)}")
            raise
    
    def find_restaurants_by_cuisine(self, cuisine: str, min_rating: float = 0.0) -> List[Restaurant]:
        """Find restaurants by cuisine type and minimum rating."""
        try:
            query = {
                "attributes.cuisine_type": cuisine,
                "overall_rating": {"$gte": min_rating}
            }
            restaurants = list(self.restaurants.find(query))
            return [Restaurant.parse_obj(r) for r in restaurants]
        except Exception as e:
            logger.error(f"Error finding restaurants by cuisine {cuisine}: {str(e)}")
            raise
    
    def find_restaurants_near_location(self, lat: float, lng: float, 
                                     max_distance_km: float = 5) -> List[Restaurant]:
        """Find restaurants near a specific location."""
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": max_distance_km * 1000  # Convert to meters
                }
            }
        }
        restaurants = list(self.restaurants.find(query))
        return [Restaurant.parse_obj(r) for r in restaurants]
    
    def close(self):
        """Close the MongoDB connection."""
        self.client.close() 