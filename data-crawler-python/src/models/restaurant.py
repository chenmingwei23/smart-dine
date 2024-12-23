"""
Data models for restaurant information.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Review(BaseModel):
    """Model for a restaurant review."""
    id_review: Optional[str] = Field(None, description="Unique identifier for the review")
    caption: Optional[str] = Field(None, description="Review text content")
    relative_date: Optional[str] = Field(None, description="When the review was posted (relative)")
    retrieval_date: Optional[datetime] = Field(None, description="When the review was retrieved")
    rating: Optional[float] = Field(None, description="Review rating (1-5)")
    username: Optional[str] = Field(None, description="Name of the reviewer")
    n_review_user: Optional[int] = Field(None, description="Number of reviews by this user")
    n_photo_user: Optional[int] = Field(None, description="Number of photos by this user")
    url_user: Optional[str] = Field(None, description="URL to user's profile")

class Location(BaseModel):
    """Model for restaurant location."""
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")

class OpeningHours(BaseModel):
    """Model for restaurant opening hours."""
    day: Optional[int] = Field(None, description="Day of week (0=Monday, 6=Sunday)")
    open_time: Optional[str] = Field(None, description="Opening time (HH:MM)")
    close_time: Optional[str] = Field(None, description="Closing time (HH:MM)")

class RestaurantAttributes(BaseModel):
    """Model for restaurant attributes and features."""
    cuisine_type: Optional[List[str]] = Field(default_factory=list, description="Types of cuisine served")
    price_level: Optional[str] = Field(None, description="Price level ($-$$$$)")
    service_speed: Optional[str] = Field(None, description="Speed of service")
    ambiance: Optional[str] = Field(None, description="Restaurant ambiance")
    noise_level: Optional[str] = Field(None, description="Noise level")
    parking_availability: Optional[str] = Field(None, description="Parking information")
    dietary_options: Optional[List[str]] = Field(default_factory=list, description="Available dietary options")
    popular_dishes: Optional[List[str]] = Field(default_factory=list, description="Popular menu items")
    peak_hours: Optional[Dict[str, str]] = Field(default_factory=dict, description="Peak hours by day")
    wait_time: Optional[str] = Field(None, description="Typical wait time")

class Restaurant(BaseModel):
    """Model for restaurant information."""
    name: Optional[str] = Field(None, description="Restaurant name")
    url: str = Field(..., description="Google Maps URL")
    location: Optional[Dict] = Field(None, description="Restaurant location")
    phone: Optional[str] = Field(None, description="Contact phone number")
    website: Optional[str] = Field(None, description="Restaurant website")
    opening_hours: Optional[List[Dict]] = Field(default_factory=list, description="Opening hours")
    overall_rating: Optional[float] = Field(None, description="Overall rating (1-5)")
    total_reviews: Optional[int] = Field(None, description="Total number of reviews")
    attributes: Optional[Dict] = Field(default_factory=dict, description="Restaurant attributes")
    photos: Optional[List[str]] = Field(default_factory=list, description="Photo URLs")
    reviews: Optional[List[Dict]] = Field(default_factory=list, description="Restaurant reviews")
    raw_data: Optional[Dict] = Field(None, description="Raw scraped data")