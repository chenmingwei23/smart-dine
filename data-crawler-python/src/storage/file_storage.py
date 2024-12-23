import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FileStorage:
    """Local file storage for restaurant data."""
    
    def __init__(self, base_dir: str = "data"):
        """Initialize file storage with base directory."""
        self.base_dir = Path(base_dir)
        self.restaurants_dir = self.base_dir / "restaurants"
        self.reviews_dir = self.base_dir / "reviews"
        self._create_directories()
        
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        self.base_dir.mkdir(exist_ok=True)
        self.restaurants_dir.mkdir(exist_ok=True)
        self.reviews_dir.mkdir(exist_ok=True)
        
    def _sanitize_filename(self, name: str) -> str:
        """Convert restaurant name to a valid filename."""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    def upsert_restaurant(self, restaurant_data: dict) -> str:
        """Save restaurant data to a JSON file."""
        try:
            # Generate a filename from the restaurant name
            name = restaurant_data.get('name', 'unknown')
            sanitized_name = self._sanitize_filename(name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{sanitized_name}_{timestamp}.json"
            
            # Extract reviews to save separately
            reviews = restaurant_data.pop('reviews', [])
            
            # Save restaurant data
            restaurant_file = self.restaurants_dir / filename
            with open(restaurant_file, 'w', encoding='utf-8') as f:
                json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
            
            # Save reviews if any
            if reviews:
                reviews_file = self.reviews_dir / f"{sanitized_name}_{timestamp}_reviews.json"
                with open(reviews_file, 'w', encoding='utf-8') as f:
                    json.dump(reviews, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved restaurant data to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving restaurant data: {str(e)}")
            raise
    
    def get_restaurant(self, filename: str) -> Optional[Dict]:
        """Get restaurant data from a file."""
        try:
            file_path = self.restaurants_dir / filename
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                restaurant_data = json.load(f)
            
            # Try to load reviews if they exist
            reviews_file = self.reviews_dir / f"{filename.replace('.json', '_reviews.json')}"
            if reviews_file.exists():
                with open(reviews_file, 'r', encoding='utf-8') as f:
                    restaurant_data['reviews'] = json.load(f)
            
            return restaurant_data
            
        except Exception as e:
            logger.error(f"Error reading restaurant data: {str(e)}")
            return None
    
    def get_all_restaurants(self) -> List[Dict]:
        """Get all restaurant data."""
        restaurants = []
        for file_path in self.restaurants_dir.glob('*.json'):
            restaurant_data = self.get_restaurant(file_path.name)
            if restaurant_data:
                restaurants.append(restaurant_data)
        return restaurants 