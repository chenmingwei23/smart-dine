from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Location(BaseModel):
    """Location schema"""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    address: str = Field(..., description="Full address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")

class RestaurantAttributes(BaseModel):
    """Restaurant attributes schema"""
    cuisine_type: List[str] = Field(default_factory=list, description="Types of cuisine served")
    price_level: Optional[str] = Field(None, description="Price level ($-$$$$)")
    service_speed: Optional[str] = Field(None, description="Speed of service")
    ambiance: Optional[str] = Field(None, description="Restaurant ambiance")
    noise_level: Optional[str] = Field(None, description="Noise level")
    parking_availability: Optional[str] = Field(None, description="Parking information")
    dietary_options: List[str] = Field(default_factory=list, description="Available dietary options")
    popular_dishes: List[str] = Field(default_factory=list, description="Popular menu items")
    peak_hours: Dict[str, str] = Field(default_factory=dict, description="Peak hours by day")
    wait_time: Optional[str] = Field(None, description="Typical wait time")

class ReviewStats(BaseModel):
    """Review statistics schema"""
    total_reviews: int = Field(..., description="Total number of reviews")
    avg_rating: float = Field(..., description="Average rating")
    rating_distribution: Dict[str, int] = Field(..., description="Distribution of ratings")

class RestaurantBase(BaseModel):
    """Base restaurant schema"""
    name: str = Field(..., description="Restaurant name")
    url: str = Field(..., description="Google Maps URL")
    location: Location
    phone: Optional[str] = Field(None, description="Contact phone number")
    website: Optional[str] = Field(None, description="Restaurant website")
    overall_rating: float = Field(..., description="Overall rating (1-5)")
    total_reviews: int = Field(..., description="Total number of reviews")
    attributes: RestaurantAttributes
    photos: List[str] = Field(default_factory=list, description="Photo URLs")

class RestaurantCreate(RestaurantBase):
    """Schema for creating a restaurant"""
    pass

class RestaurantUpdate(BaseModel):
    """Schema for updating a restaurant"""
    name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    overall_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    attributes: Optional[RestaurantAttributes] = None
    photos: Optional[List[str]] = None

class RestaurantInDB(RestaurantBase):
    """Schema for restaurant in database"""
    id: str = Field(..., alias="_id")
    review_stats: Optional[ReviewStats] = None

    class Config:
        allow_population_by_field_name = True

class RestaurantSearchResults(BaseModel):
    """Schema for restaurant search results"""
    total: int
    restaurants: List[RestaurantInDB]
    page: int
    total_pages: int 