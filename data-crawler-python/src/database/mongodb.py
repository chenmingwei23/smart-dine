"""
MongoDB database operations.
Handles all database interactions for storing and retrieving restaurant data.
"""

from typing import List, Optional
import ssl
from urllib.parse import quote_plus

from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from models.restaurant import Restaurant, Review
from config.settings import settings

class MongoDBClient:
    """MongoDB client for restaurant data storage."""
    
    def __init__(self, mongo_url: str = None, db_name: str = None):
        """Initialize MongoDB client with Atlas support.
        
        Args:
            mongo_url: MongoDB connection URL. If None, uses settings.mongodb_url
            db_name: Database name. If None, uses settings.mongodb_db
        """
        self.mongo_url = mongo_url or settings.mongodb_url
        self.db_name = db_name or settings.mongodb_db
        
        try:
            # Configure MongoDB client with proper SSL settings for Atlas
            self.client = MongoClient(
                self.mongo_url,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            self.restaurants: Collection = self.db[settings.mongodb_collection_restaurants]
            self.reviews: Collection = self.db[settings.mongodb_collection_reviews]
            
            # Create indexes
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"Failed to connect to MongoDB Atlas: {str(e)}")
    
    def _create_indexes(self):
        """Create necessary database indexes."""
        try:
            self.restaurants.create_index("url", unique=True)
            self.reviews.create_index("id_review", unique=True)
            self.restaurants.create_index([("location.lat", 1), ("location.lng", 1)])
            self.restaurants.create_index("cuisine_type")
            self.restaurants.create_index("overall_rating")
        except Exception as e:
            raise Exception(f"Failed to create indexes: {str(e)}")
    
    def upsert_restaurant(self, restaurant: Restaurant) -> str:
        """Upsert a restaurant and return its ID."""
        restaurant_dict = restaurant.dict(by_alias=True)
        reviews = restaurant_dict.pop("reviews", [])
        
        # Upsert restaurant
        result = self.restaurants.update_one(
            {"url": restaurant.url},
            {"$set": restaurant_dict},
            upsert=True
        )
        
        # Get restaurant ID
        if result.upserted_id:
            restaurant_id = result.upserted_id
        else:
            restaurant_id = self.restaurants.find_one({"url": restaurant.url})["_id"]
        
        # Bulk upsert reviews
        if reviews:
            operations = []
            for review in reviews:
                review_dict = review.dict(by_alias=True)
                review_dict["restaurant_id"] = restaurant_id
                operations.append(
                    UpdateOne(
                        {"_id": review_dict["_id"]},
                        {"$set": review_dict},
                        upsert=True
                    )
                )
            if operations:
                self.reviews.bulk_write(operations)
        
        return str(restaurant_id)
    
    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        """Get a restaurant by ID with its reviews."""
        restaurant_dict = self.restaurants.find_one({"_id": restaurant_id})
        if not restaurant_dict:
            return None
            
        reviews = list(self.reviews.find({"restaurant_id": restaurant_id}))
        restaurant_dict["reviews"] = reviews
        
        return Restaurant.parse_obj(restaurant_dict)
    
    def get_restaurants(self, skip: int = 0, limit: int = 20) -> List[Restaurant]:
        """Get a list of restaurants without reviews."""
        restaurants = list(self.restaurants.find().skip(skip).limit(limit))
        return [Restaurant.parse_obj(r) for r in restaurants]
    
    def get_restaurant_by_url(self, url: str) -> Optional[Restaurant]:
        """Get a restaurant by its Google Maps URL."""
        restaurant_dict = self.restaurants.find_one({"url": url})
        if not restaurant_dict:
            return None
            
        reviews = list(self.reviews.find({"restaurant_id": restaurant_dict["_id"]}))
        restaurant_dict["reviews"] = reviews
        
        return Restaurant.parse_obj(restaurant_dict)
    
    def find_restaurants_by_cuisine(self, cuisine: str, 
                                  min_rating: float = 0.0) -> List[Restaurant]:
        """Find restaurants by cuisine type and minimum rating."""
        query = {
            "attributes.cuisine_type": cuisine,
            "overall_rating": {"$gte": min_rating}
        }
        restaurants = list(self.restaurants.find(query))
        return [Restaurant.parse_obj(r) for r in restaurants]
    
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