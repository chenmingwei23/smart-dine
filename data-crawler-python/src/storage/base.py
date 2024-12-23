from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class StorageInterface(ABC):
    """Base interface for storage implementations."""
    
    @abstractmethod
    def upsert_restaurant(self, restaurant_data: dict) -> str:
        """Save restaurant data and return its ID."""
        pass
    
    @abstractmethod
    def upsert_reviews(self, reviews: List[dict]) -> None:
        """Save multiple review documents."""
        pass
    
    @abstractmethod
    def get_restaurant(self, restaurant_id: str) -> Optional[Dict]:
        """Get restaurant data by ID."""
        pass
    
    @abstractmethod
    def get_reviews(self, restaurant_id: str) -> List[Dict]:
        """Get all reviews for a restaurant."""
        pass 