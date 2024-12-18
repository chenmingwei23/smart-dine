from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class UserPreferences(BaseModel):
    favorite_cuisines: List[str] = []
    dietary_restrictions: List[str] = []
    price_range: List[int] = [1, 2, 3, 4]  # 1-4 representing price levels
    preferred_locations: List[str] = []
    favorite_restaurants: List[str] = []

class User(BaseModel):
    id: str = Field(..., description="Unique identifier")
    email: EmailStr
    username: str
    hashed_password: str
    preferences: UserPreferences
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime]
    is_active: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "username": "foodie_user",
                "hashed_password": "hashed_password_string",
                "preferences": {
                    "favorite_cuisines": ["Italian", "Japanese"],
                    "dietary_restrictions": ["vegetarian"],
                    "price_range": [2, 3],
                    "preferred_locations": ["Downtown", "Midtown"],
                    "favorite_restaurants": ["restaurant_id_1", "restaurant_id_2"]
                }
            }
        } 