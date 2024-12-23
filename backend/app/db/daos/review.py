from typing import List, Dict, Optional
from ..base import BaseDAO
from bson import ObjectId
from datetime import datetime

class ReviewDAO(BaseDAO):
    """Data Access Object for review operations"""
    
    def __init__(self):
        super().__init__("reviews")
    
    async def find_by_id(self, review_id: str) -> Optional[Dict]:
        """Find review by ID"""
        return await self.find_one({"_id": ObjectId(review_id)})
    
    async def find_by_restaurant(self, 
                               restaurant_id: str, 
                               skip: int = 0, 
                               limit: int = 20,
                               min_rating: Optional[float] = None,
                               sort_by_date: bool = True) -> Dict:
        """Find reviews for a specific restaurant"""
        query = {"restaurant_id": restaurant_id}
        if min_rating:
            query["rating"] = {"$gte": min_rating}
            
        sort_field = "retrieval_date" if sort_by_date else "rating"
        sort_order = -1  # descending
        
        total = await self.count(query)
        reviews = await self.find_many(
            query, 
            skip=skip, 
            limit=limit,
            sort=[(sort_field, sort_order)]
        )
        
        return {
            "total": total,
            "reviews": reviews,
            "page": skip // limit + 1,
            "total_pages": (total + limit - 1) // limit
        }
    
    async def get_review_stats(self, restaurant_id: str) -> Dict:
        """Get review statistics for a restaurant"""
        pipeline = [
            {"$match": {"restaurant_id": restaurant_id}},
            {
                "$group": {
                    "_id": None,
                    "total_reviews": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"},
                    "rating_distribution": {
                        "$push": "$rating"
                    }
                }
            }
        ]
        
        stats = await self.aggregate(pipeline)
        if not stats:
            return {}
            
        result = stats[0]
        # Calculate rating distribution
        ratings = result.pop("rating_distribution", [])
        distribution = {
            "5": len([r for r in ratings if r == 5]),
            "4": len([r for r in ratings if 4 <= r < 5]),
            "3": len([r for r in ratings if 3 <= r < 4]),
            "2": len([r for r in ratings if 2 <= r < 3]),
            "1": len([r for r in ratings if r < 2])
        }
        result["rating_distribution"] = distribution
        
        return result
    
    async def find_latest_reviews(self, 
                                limit: int = 20, 
                                min_rating: Optional[float] = None) -> List[Dict]:
        """Get latest reviews across all restaurants"""
        query = {}
        if min_rating:
            query["rating"] = {"$gte": min_rating}
            
        return await self.find_many(
            query,
            limit=limit,
            sort=[("retrieval_date", -1)]
        )
    
    async def find_top_reviewers(self, limit: int = 10) -> List[Dict]:
        """Find users with most reviews"""
        pipeline = [
            {
                "$group": {
                    "_id": "$reviewer.username",
                    "review_count": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"},
                    "latest_review": {"$max": "$retrieval_date"}
                }
            },
            {"$sort": {"review_count": -1}},
            {"$limit": limit}
        ]
        return await self.aggregate(pipeline)
    
    async def search_reviews(self,
                           search_text: str,
                           restaurant_id: Optional[str] = None,
                           min_rating: Optional[float] = None,
                           skip: int = 0,
                           limit: int = 20) -> Dict:
        """Search reviews with text search"""
        query = {"$text": {"$search": search_text}}
        
        if restaurant_id:
            query["restaurant_id"] = restaurant_id
        if min_rating:
            query["rating"] = {"$gte": min_rating}
            
        total = await self.count(query)
        reviews = await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("score", {"$meta": "textScore"})]
        )
        
        return {
            "total": total,
            "reviews": reviews,
            "page": skip // limit + 1,
            "total_pages": (total + limit - 1) // limit
        }
    
    async def create_review(self, review_data: Dict) -> str:
        """Create a new review"""
        review_data["retrieval_date"] = datetime.utcnow()
        return await self.insert_one(review_data)
    
    async def update_review(self, review_id: str, update_data: Dict) -> bool:
        """Update a review"""
        result = await self.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_data}
        )
        return result > 0
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete a review"""
        result = await self.delete_one({"_id": ObjectId(review_id)})
        return result > 0 