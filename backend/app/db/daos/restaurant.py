from typing import List, Dict, Optional
from ..base import BaseDAO
from bson import ObjectId

class RestaurantDAO(BaseDAO):
    """Data Access Object for restaurant operations"""
    
    def __init__(self):
        super().__init__("restaurants")
    
    async def find_by_id(self, restaurant_id: str) -> Optional[Dict]:
        """Find restaurant by ID"""
        return await self.find_one({"_id": ObjectId(restaurant_id)})
    
    async def find_by_name(self, name: str) -> Optional[Dict]:
        """Find restaurant by name"""
        return await self.find_one({"name": {"$regex": name, "$options": "i"}})
    
    async def find_by_cuisine(self, cuisine_type: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find restaurants by cuisine type"""
        query = {"attributes.cuisine_type": {"$in": [cuisine_type]}}
        return await self.find_many(query, skip=skip, limit=limit, sort=[("overall_rating", -1)])
    
    async def find_by_location(self, lat: float, lng: float, radius_km: float = 5) -> List[Dict]:
        """Find restaurants within radius of coordinates"""
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": radius_km * 1000  # Convert km to meters
                }
            }
        }
        return await self.find_many(query)
    
    async def find_by_price_level(self, price_level: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find restaurants by price level"""
        query = {"attributes.price_level": price_level}
        return await self.find_many(query, skip=skip, limit=limit)
    
    async def find_top_rated(self, min_rating: float = 4.0, min_reviews: int = 10, limit: int = 20) -> List[Dict]:
        """Find top rated restaurants"""
        query = {
            "overall_rating": {"$gte": min_rating},
            "total_reviews": {"$gte": min_reviews}
        }
        return await self.find_many(query, limit=limit, sort=[("overall_rating", -1)])
    
    async def search_restaurants(self, 
                               search_text: str,
                               cuisine_types: Optional[List[str]] = None,
                               price_levels: Optional[List[str]] = None,
                               min_rating: Optional[float] = None,
                               skip: int = 0,
                               limit: int = 20) -> Dict:
        """Search restaurants with multiple criteria"""
        query = {"$text": {"$search": search_text}} if search_text else {}
        
        if cuisine_types:
            query["attributes.cuisine_type"] = {"$in": cuisine_types}
        if price_levels:
            query["attributes.price_level"] = {"$in": price_levels}
        if min_rating:
            query["overall_rating"] = {"$gte": min_rating}
            
        total = await self.count(query)
        restaurants = await self.find_many(query, skip=skip, limit=limit, 
                                         sort=[("overall_rating", -1)])
        
        return {
            "total": total,
            "restaurants": restaurants,
            "page": skip // limit + 1,
            "total_pages": (total + limit - 1) // limit
        }
    
    async def get_restaurant_stats(self) -> Dict:
        """Get restaurant statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_restaurants": {"$sum": 1},
                    "avg_rating": {"$avg": "$overall_rating"},
                    "total_reviews": {"$sum": "$total_reviews"},
                    "cuisine_types": {"$addToSet": "$attributes.cuisine_type"},
                }
            }
        ]
        stats = await self.aggregate(pipeline)
        return stats[0] if stats else {}
    
    async def create_restaurant(self, restaurant_data: Dict) -> str:
        """Create a new restaurant"""
        return await self.insert_one(restaurant_data)
    
    async def update_restaurant(self, restaurant_id: str, update_data: Dict) -> bool:
        """Update a restaurant"""
        result = await self.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": update_data}
        )
        return result > 0 