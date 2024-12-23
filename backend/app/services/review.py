from typing import List, Optional, Dict
from fastapi import HTTPException
from ..db.daos import restaurant_dao, review_dao
from ..schemas.review import ReviewCreate, ReviewUpdate

class ReviewService:
    """Service for review-related operations"""

    @staticmethod
    async def search_reviews(
        search_text: str,
        restaurant_id: Optional[str] = None,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Search reviews with text search"""
        try:
            if restaurant_id:
                # Verify restaurant exists
                restaurant = await restaurant_dao.find_by_id(restaurant_id)
                if not restaurant:
                    raise HTTPException(status_code=404, detail="Restaurant not found")
            
            return await review_dao.search_reviews(
                search_text=search_text,
                restaurant_id=restaurant_id,
                min_rating=min_rating,
                skip=skip,
                limit=limit
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_latest_reviews(
        limit: int = 20,
        min_rating: Optional[float] = None
    ) -> List[Dict]:
        """Get latest reviews across all restaurants"""
        try:
            return await review_dao.find_latest_reviews(
                limit=limit,
                min_rating=min_rating
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_top_reviewers(limit: int = 10) -> List[Dict]:
        """Get users with most reviews"""
        try:
            return await review_dao.find_top_reviewers(limit=limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_review_by_id(review_id: str) -> Optional[Dict]:
        """Get review by ID"""
        try:
            review = await review_dao.find_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            return review
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_review(review: ReviewCreate) -> Dict:
        """Create a new review"""
        try:
            # Verify restaurant exists
            restaurant = await restaurant_dao.find_by_id(review.restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            
            # Create review
            review_id = await review_dao.create_review(review.dict())
            
            # Update restaurant rating and review count
            # This should be done in a transaction in production
            total_reviews = restaurant["total_reviews"] + 1
            new_rating = (restaurant["overall_rating"] * (total_reviews - 1) + review.rating) / total_reviews
            
            await restaurant_dao.update_restaurant(
                review.restaurant_id,
                {
                    "total_reviews": total_reviews,
                    "overall_rating": round(new_rating, 2)
                }
            )
            
            return await review_dao.find_by_id(review_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_review(review_id: str, review: ReviewUpdate) -> Dict:
        """Update a review"""
        try:
            # Check if review exists
            existing = await review_dao.find_by_id(review_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Review not found")
            
            # Update only provided fields
            update_data = review.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )
            
            # If rating is updated, update restaurant rating
            if "rating" in update_data:
                restaurant = await restaurant_dao.find_by_id(existing["restaurant_id"])
                if restaurant:
                    old_rating = existing["rating"]
                    new_rating = update_data["rating"]
                    total_reviews = restaurant["total_reviews"]
                    
                    updated_rating = (
                        (restaurant["overall_rating"] * total_reviews - old_rating + new_rating)
                        / total_reviews
                    )
                    
                    await restaurant_dao.update_restaurant(
                        existing["restaurant_id"],
                        {"overall_rating": round(updated_rating, 2)}
                    )
            
            success = await review_dao.update_review(review_id, update_data)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update review"
                )
            
            return await review_dao.find_by_id(review_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_review(review_id: str) -> bool:
        """Delete a review"""
        try:
            # Check if review exists
            review = await review_dao.find_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
            # Delete review
            success = await review_dao.delete_review(review_id)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete review"
                )
            
            # Update restaurant rating and review count
            restaurant = await restaurant_dao.find_by_id(review["restaurant_id"])
            if restaurant:
                total_reviews = restaurant["total_reviews"] - 1
                if total_reviews > 0:
                    new_rating = (
                        (restaurant["overall_rating"] * (total_reviews + 1) - review["rating"])
                        / total_reviews
                    )
                else:
                    new_rating = 0
                
                await restaurant_dao.update_restaurant(
                    review["restaurant_id"],
                    {
                        "total_reviews": total_reviews,
                        "overall_rating": round(new_rating, 2)
                    }
                )
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Create service instance
review_service = ReviewService() 