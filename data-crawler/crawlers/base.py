from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator
from ..models.restaurant import Restaurant
from ..config import settings
import logging
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.headers: Dict[str, str] = {}
        self.retry_count: int = 0
        self.max_retries: int = settings.MAX_RETRIES

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def search_restaurants(self, location: Dict[str, float], radius_km: int = None) -> Generator[Dict, None, None]:
        """Search for restaurants in a given location"""
        pass

    @abstractmethod
    async def get_restaurant_details(self, restaurant_id: str) -> Dict:
        """Get detailed information about a specific restaurant"""
        pass

    @abstractmethod
    async def get_reviews(self, restaurant_id: str) -> List[Dict]:
        """Get reviews for a specific restaurant"""
        pass

    async def _make_request(self, url: str, params: Dict = None, method: str = "GET") -> Dict:
        """Make an HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method, 
                    url, 
                    params=params,
                    timeout=settings.REQUEST_TIMEOUT
                ) as response:
                    if response.status == 429:  # Rate limit
                        wait_time = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    response.raise_for_status()
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        raise Exception("Max retries exceeded")

    def _normalize_restaurant_data(self, raw_data: Dict[str, Any], source: str) -> Restaurant:
        """Convert raw API data to normalized Restaurant model"""
        try:
            # Basic validation
            if not raw_data.get('name') or not raw_data.get('location'):
                raise ValueError("Missing required fields")

            # Create normalized restaurant object
            restaurant_data = {
                'id': raw_data.get('id') or raw_data.get('place_id'),
                'name': raw_data['name'],
                'location': {
                    'lat': float(raw_data['location']['lat']),
                    'lng': float(raw_data['location']['lng']),
                    'address': raw_data['location'].get('address', ''),
                    'city': raw_data['location'].get('city', ''),
                    'state': raw_data['location'].get('state', ''),
                    'country': raw_data['location'].get('country', ''),
                    'postal_code': raw_data['location'].get('postal_code', '')
                },
                'phone': raw_data.get('phone'),
                'website': raw_data.get('website'),
                'rating': float(raw_data.get('rating', 0)),
                'review_count': int(raw_data.get('review_count', 0)),
                'data_sources': [source],
                'last_updated': datetime.utcnow(),
                'raw_data': raw_data
            }

            return Restaurant(**restaurant_data)

        except Exception as e:
            logger.error(f"Error normalizing restaurant data: {str(e)}")
            raise

    async def process_location(self, location: Dict[str, float], radius_km: int = None) -> List[Restaurant]:
        """Process a single location and return normalized restaurant data"""
        restaurants = []
        async for restaurant_data in self.search_restaurants(location, radius_km):
            try:
                # Get additional details
                details = await self.get_restaurant_details(restaurant_data['id'])
                reviews = await self.get_reviews(restaurant_data['id'])
                
                # Merge all data
                full_data = {
                    **restaurant_data,
                    **details,
                    'reviews': reviews
                }
                
                # Normalize and add to results
                normalized_restaurant = self._normalize_restaurant_data(full_data, self.__class__.__name__)
                restaurants.append(normalized_restaurant)
                
            except Exception as e:
                logger.error(f"Error processing restaurant {restaurant_data.get('name', 'Unknown')}: {str(e)}")
                continue
                
        return restaurants 