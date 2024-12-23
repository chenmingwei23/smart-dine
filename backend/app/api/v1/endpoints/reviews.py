from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ....schemas.review import (
    ReviewInDB,
    ReviewCreate,
    ReviewUpdate,
    ReviewSearchResults,
    ReviewStats,
    TopReviewer
)
from ....core.config import settings
from ....services.review import review_service

router = APIRouter()

@router.get("/", response_model=ReviewSearchResults)
async def search_reviews(
    search_text: str = Query(..., min_length=1),
    restaurant_id: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50)
):
    """
    Search reviews with text search.
    """
    return await review_service.search_reviews(
        search_text=search_text,
        restaurant_id=restaurant_id,
        min_rating=min_rating,
        skip=skip,
        limit=limit
    )

@router.get("/latest", response_model=List[ReviewInDB])
async def get_latest_reviews(
    limit: int = Query(default=20, le=50),
    min_rating: Optional[float] = Query(None, ge=0, le=5)
):
    """
    Get latest reviews across all restaurants.
    """
    return await review_service.get_latest_reviews(
        limit=limit,
        min_rating=min_rating
    )

@router.get("/top-reviewers", response_model=List[TopReviewer])
async def get_top_reviewers(
    limit: int = Query(default=10, le=50)
):
    """
    Get users with most reviews.
    """
    return await review_service.get_top_reviewers(limit=limit)

@router.get("/{review_id}", response_model=ReviewInDB)
async def get_review(review_id: str):
    """
    Get review by ID.
    """
    return await review_service.get_review_by_id(review_id)

@router.post("/", response_model=ReviewInDB)
async def create_review(review: ReviewCreate):
    """
    Create a new review.
    """
    return await review_service.create_review(review)

@router.put("/{review_id}", response_model=ReviewInDB)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate
):
    """
    Update a review.
    """
    return await review_service.update_review(review_id, review_update)

@router.delete("/{review_id}")
async def delete_review(review_id: str):
    """
    Delete a review.
    """
    return await review_service.delete_review(review_id) 