from typing import List, Optional, Dict
from fastapi import HTTPException
from ..db.daos import restaurant_dao, review_dao
from ..schemas.restaurant import RestaurantCreate, RestaurantUpdate

class RestaurantService:
    """Service for restaurant-related operations"""

    @staticmethod
    async def get_restaurants(
        cuisine: Optional[str] = None,
        price_level: Optional[str] = None,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict:
        """Get restaurants with filters"""
        try:
            if cuisine:
                restaurants = await restaurant_dao.find_by_cuisine(cuisine, skip=skip, limit=limit)
                total = await restaurant_dao.count({"attributes.cuisine_type": {"$in": [cuisine]}})
            else:
                search_result = await restaurant_dao.search_restaurants(
                    search_text="",
                    cuisine_types=[cuisine] if cuisine else None,
                    price_levels=[price_level] if price_level else None,
                    min_rating=min_rating,
                    skip=skip,
                    limit=limit
                )
                return search_result
                
            return {
                "total": total,
                "restaurants": restaurants,
                "page": skip // limit + 1,
                "total_pages": (total + limit - 1) // limit
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict]:
        """Get restaurant by ID with reviews summary"""
        try:
            restaurant = await restaurant_dao.find_by_id(restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            
            # Get review statistics
            review_stats = await review_dao.get_review_stats(restaurant_id)
            restaurant["review_stats"] = review_stats
            
            return restaurant
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_restaurant_reviews(
        restaurant_id: str,
        skip: int = 0,
        limit: int = 10,
        min_rating: Optional[float] = None,
        sort_by_date: bool = True
    ) -> Dict:
        """Get reviews for a restaurant"""
        try:
            # Verify restaurant exists
            restaurant = await restaurant_dao.find_by_id(restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            
            return await review_dao.find_by_restaurant(
                restaurant_id=restaurant_id,
                skip=skip,
                limit=limit,
                min_rating=min_rating,
                sort_by_date=sort_by_date
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_popular_restaurants(limit: int = 10) -> List[Dict]:
        """Get popular restaurants based on rating and review count"""
        try:
            return await restaurant_dao.find_top_rated(
                min_rating=4.0,
                min_reviews=10,
                limit=limit
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def search_restaurants(
        query: str,
        cuisine_types: Optional[List[str]] = None,
        price_levels: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict:
        """Search restaurants with text query and filters"""
        try:
            return await restaurant_dao.search_restaurants(
                search_text=query,
                cuisine_types=cuisine_types,
                price_levels=price_levels,
                min_rating=min_rating,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_restaurant_stats() -> Dict:
        """Get restaurant statistics"""
        try:
            return await restaurant_dao.get_restaurant_stats()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_restaurant(restaurant: RestaurantCreate) -> Dict:
        """Create a new restaurant"""
        try:
            # Check if restaurant with same name exists
            existing = await restaurant_dao.find_by_name(restaurant.name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Restaurant with this name already exists"
                )
            
            restaurant_id = await restaurant_dao.create_restaurant(restaurant.dict())
            return await restaurant_dao.find_by_id(restaurant_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_restaurant(restaurant_id: str, restaurant: RestaurantUpdate) -> Dict:
        """Update a restaurant"""
        try:
            # Check if restaurant exists
            existing = await restaurant_dao.find_by_id(restaurant_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            
            # Update only provided fields
            update_data = restaurant.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )
            
            success = await restaurant_dao.update_restaurant(restaurant_id, update_data)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update restaurant"
                )
            
            return await restaurant_dao.find_by_id(restaurant_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Create service instance
restaurant_service = RestaurantService() 