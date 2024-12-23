import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.storage.base import StorageInterface

logger = logging.getLogger(__name__)

class FileStorage(StorageInterface):
    """File-based storage for testing."""
    
    def __init__(self, base_dir: str = "tests/data"):
        """Initialize file storage with base directory."""
        self.base_dir = Path(base_dir)
        self.restaurants_dir = self.base_dir / "restaurants"
        self.reviews_dir = self.base_dir / "reviews"
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        self.base_dir.mkdir(exist_ok=True, parents=True)
        self.restaurants_dir.mkdir(exist_ok=True)
        self.reviews_dir.mkdir(exist_ok=True)
    
    def upsert_restaurant(self, restaurant_data: dict) -> str:
        """Save restaurant data to a JSON file."""
        try:
            restaurant_id = restaurant_data.get('_id')
            if not restaurant_id:
                raise ValueError("Restaurant data must include _id field")
            
            # Remove reviews if present, they'll be saved separately
            reviews = restaurant_data.pop('reviews', [])
            
            # Save restaurant data
            restaurant_file = self.restaurants_dir / f"{restaurant_id}.json"
            with open(restaurant_file, 'w', encoding='utf-8') as f:
                json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
            
            # Save reviews if any
            if reviews:
                self.upsert_reviews(reviews)
            
            logger.info(f"Saved restaurant to {restaurant_file}")
            return restaurant_id
            
        except Exception as e:
            logger.error(f"Error saving restaurant data: {str(e)}")
            raise
    
    def upsert_reviews(self, reviews: List[dict]) -> None:
        """Save reviews to JSON files."""
        try:
            for review in reviews:
                review_id = review.get('_id')
                if not review_id:
                    continue
                
                review_file = self.reviews_dir / f"{review_id}.json"
                with open(review_file, 'w', encoding='utf-8') as f:
                    json.dump(review, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(reviews)} reviews")
            
        except Exception as e:
            logger.error(f"Error saving reviews: {str(e)}")
            raise
    
    def get_restaurant(self, restaurant_id: str) -> Optional[Dict]:
        """Get restaurant data from file."""
        try:
            restaurant_file = self.restaurants_dir / f"{restaurant_id}.json"
            if not restaurant_file.exists():
                return None
            
            with open(restaurant_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error reading restaurant data: {str(e)}")
            return None
    
    def get_reviews(self, restaurant_id: str) -> List[Dict]:
        """Get all reviews for a restaurant."""
        try:
            reviews = []
            for review_file in self.reviews_dir.glob(f"{restaurant_id}_review_*.json"):
                with open(review_file, 'r', encoding='utf-8') as f:
                    reviews.append(json.load(f))
            return reviews
            
        except Exception as e:
            logger.error(f"Error reading reviews: {str(e)}")
            return [] 