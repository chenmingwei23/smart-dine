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

class RestaurantAttributes(BaseModel):
    cuisine_type: List[str]
    price_level: int
    service_speed: Optional[str]
    ambiance: Optional[List[str]]
    noise_level: Optional[str]
    parking_availability: Optional[str]
    dietary_options: Optional[List[str]]
    popular_dishes: Optional[List[str]]
    peak_hours: Optional[Dict[str, List[str]]]
    wait_time: Optional[Dict[str, int]]

class Restaurant(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str
    location: Location
    rating: float
    review_count: int
    attributes: RestaurantAttributes
    photos: Optional[List[str]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "name": "Sushi Paradise",
                "location": {
                    "lat": 40.7128,
                    "lng": -74.0060,
                    "address": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "country": "USA",
                    "postal_code": "10001"
                },
                "rating": 4.5,
                "review_count": 100,
                "attributes": {
                    "cuisine_type": ["Japanese", "Sushi"],
                    "price_level": 3,
                    "service_speed": "fast",
                    "ambiance": ["modern", "cozy"],
                    "noise_level": "moderate",
                    "parking_availability": "street",
                    "dietary_options": ["vegetarian", "gluten-free"],
                    "popular_dishes": ["Dragon Roll", "Miso Soup"],
                    "peak_hours": {
                        "weekday": ["12:00-14:00", "18:00-20:00"],
                        "weekend": ["18:00-21:00"]
                    },
                    "wait_time": {
                        "lunch": 15,
                        "dinner": 30
                    }
                }
            }
        } 