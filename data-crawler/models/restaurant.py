from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Location(BaseModel):
    lat: float
    lng: float
    address: str
    city: str
    state: str
    country: str
    postal_code: str

class OpeningHours(BaseModel):
    day: int  # 0-6 (Monday-Sunday)
    open_time: str
    close_time: str
    is_overnight: bool = False

class Review(BaseModel):
    source: str  # "google", "yelp", etc.
    rating: float
    text: str
    date: datetime
    user_name: Optional[str]
    likes: Optional[int]

class RestaurantAttributes(BaseModel):
    cuisine_type: List[str]
    price_level: int  # 1-4
    service_speed: Optional[str]  # "fast", "medium", "slow"
    ambiance: Optional[List[str]]
    noise_level: Optional[str]  # "quiet", "moderate", "loud"
    parking_availability: Optional[str]
    dietary_options: Optional[List[str]]
    popular_dishes: Optional[List[str]]
    peak_hours: Optional[Dict[str, List[str]]]
    wait_time: Optional[Dict[str, int]]  # minutes by time of day

class Restaurant(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str
    location: Location
    phone: Optional[str]
    website: Optional[str]
    opening_hours: List[OpeningHours]
    rating: float
    review_count: int
    reviews: List[Review]
    attributes: RestaurantAttributes
    photos: Optional[List[str]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str]  # ["google", "yelp", etc.]
    raw_data: Dict = Field(default_factory=dict)  # Store original crawled data

    class Config:
        allow_population_by_field_name = True 