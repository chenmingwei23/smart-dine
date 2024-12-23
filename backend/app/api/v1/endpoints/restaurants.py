from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ....schemas.restaurant import (
    RestaurantInDB,
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantSearchResults,
)
from ....schemas.review import ReviewSearchResults, ReviewStats
from ....core.config import settings
from ....services.restaurant import restaurant_service

router = APIRouter()

@router.get("/", response_model=RestaurantSearchResults)
async def get_restaurants(
    cuisine: Optional[str] = None,
    price_level: Optional[str] = Query(None, description="Price level ($-$$$$)"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    limit: int = Query(default=10, le=50),
    skip: int = Query(default=0, ge=0)
):
    """
    Get restaurants with optional filters.
    """
    return await restaurant_service.get_restaurants(
        cuisine=cuisine,
        price_level=price_level,
        min_rating=min_rating,
        skip=skip,
        limit=limit
    )

@router.get("/{restaurant_id}", response_model=RestaurantInDB)
async def get_restaurant(restaurant_id: str):
    """
    Get restaurant details by ID.
    """
    return await restaurant_service.get_restaurant_by_id(restaurant_id)

@router.get("/{restaurant_id}/reviews", response_model=ReviewSearchResults)
async def get_restaurant_reviews(
    restaurant_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by_date: bool = Query(default=True)
):
    """
    Get reviews for a restaurant.
    """
    return await restaurant_service.get_restaurant_reviews(
        restaurant_id=restaurant_id,
        skip=skip,
        limit=limit,
        min_rating=min_rating,
        sort_by_date=sort_by_date
    )

@router.get("/popular", response_model=List[RestaurantInDB])
async def get_popular_restaurants(
    limit: int = Query(default=10, le=50)
):
    """
    Get popular restaurants based on rating and review count.
    """
    return await restaurant_service.get_popular_restaurants(limit=limit)

@router.get("/search", response_model=RestaurantSearchResults)
async def search_restaurants(
    query: str = Query(..., min_length=1),
    cuisine_types: Optional[List[str]] = Query(None),
    price_levels: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50)
):
    """
    Search restaurants with text query and filters.
    """
    return await restaurant_service.search_restaurants(
        query=query,
        cuisine_types=cuisine_types,
        price_levels=price_levels,
        min_rating=min_rating,
        skip=skip,
        limit=limit
    )

@router.get("/stats", response_model=dict)
async def get_restaurant_stats():
    """
    Get restaurant statistics.
    """
    return await restaurant_service.get_restaurant_stats()

@router.post("/", response_model=RestaurantInDB)
async def create_restaurant(restaurant: RestaurantCreate):
    """
    Create a new restaurant.
    """
    return await restaurant_service.create_restaurant(restaurant)

@router.put("/{restaurant_id}", response_model=RestaurantInDB)
async def update_restaurant(
    restaurant_id: str,
    restaurant_update: RestaurantUpdate
):
    """
    Update a restaurant.
    """
    return await restaurant_service.update_restaurant(restaurant_id, restaurant_update) 