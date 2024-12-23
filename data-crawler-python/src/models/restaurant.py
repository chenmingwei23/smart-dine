"""
Restaurant data models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Location(BaseModel):
    """Restaurant location model."""
    lat: float
    lng: float
    address: str
    city: str
    state: str
    country: str
    postal_code: str

class OpeningHours(BaseModel):
    """Restaurant opening hours model."""
    day: int  # 0-6 (Monday-Sunday)
    open_time: str
    close_time: str
    is_overnight: bool = False

class Review(BaseModel):
    """Restaurant review model."""
    id_review: str = Field(..., alias="_id")
    source: str = "google"  # "google", "yelp", etc.
    rating: float
    caption: Optional[str]
    relative_date: str
    timestamp: datetime
    username: Optional[str]
    n_review_user: Optional[int]
    n_photo_user: Optional[int]
    url_user: Optional[str]
    likes: Optional[int]

class RestaurantAttributes(BaseModel):
    """Additional restaurant attributes model."""
    cuisine_type: List[str] = []
    price_level: Optional[int]  # 1-4
    service_speed: Optional[str]  # "fast", "medium", "slow"
    ambiance: Optional[List[str]]
    noise_level: Optional[str]  # "quiet", "moderate", "loud"
    parking_availability: Optional[str]
    dietary_options: Optional[List[str]]
    popular_dishes: Optional[List[str]]
    peak_hours: Optional[Dict[str, List[str]]]
    wait_time: Optional[Dict[str, int]]  # minutes by time of day

class Restaurant(BaseModel):
    """Main restaurant model."""
    id: str = Field(..., alias="_id")
    name: str
    location: Location
    phone: Optional[str]
    website: Optional[str]
    opening_hours: List[OpeningHours] = []
    overall_rating: float
    total_reviews: int
    reviews: List[Review] = []
    attributes: RestaurantAttributes = Field(default_factory=RestaurantAttributes)
    photos: Optional[List[str]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = ["google"]  # ["google", "yelp", etc.]
    raw_data: Dict = Field(default_factory=dict)  # Store original crawled data
    url: str  # Google Maps URL

    class Config:
        allow_population_by_field_name = True 