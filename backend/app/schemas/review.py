from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ReviewerProfile(BaseModel):
    """Reviewer profile schema"""
    username: str = Field(..., description="Name of the reviewer")
    n_review_user: Optional[int] = Field(None, description="Number of reviews by this user")
    n_photo_user: Optional[int] = Field(None, description="Number of photos by this user")
    url_user: Optional[str] = Field(None, description="URL to user's profile")

class ReviewBase(BaseModel):
    """Base review schema"""
    restaurant_id: str = Field(..., description="ID of the restaurant")
    caption: str = Field(..., description="Review text content")
    rating: float = Field(..., ge=1, le=5, description="Review rating (1-5)")
    reviewer: ReviewerProfile
    retrieval_date: datetime = Field(..., description="When the review was retrieved")

class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    pass

class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    caption: Optional[str] = None
    rating: Optional[float] = Field(None, ge=1, le=5)

class ReviewInDB(ReviewBase):
    """Schema for review in database"""
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True

class ReviewSearchResults(BaseModel):
    """Schema for review search results"""
    total: int
    reviews: List[ReviewInDB]
    page: int
    total_pages: int

class ReviewStats(BaseModel):
    """Schema for review statistics"""
    total_reviews: int = Field(..., description="Total number of reviews")
    avg_rating: float = Field(..., description="Average rating")
    rating_distribution: Dict[str, int] = Field(..., description="Distribution of ratings")

class TopReviewer(BaseModel):
    """Schema for top reviewer"""
    username: str = Field(..., description="Reviewer username")
    review_count: int = Field(..., description="Number of reviews")
    avg_rating: float = Field(..., description="Average rating given")
    latest_review: datetime = Field(..., description="Date of latest review") 