from typing import Dict, List, Generator
from .base import BaseCrawler
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class GoogleMapsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.headers = {
            "Accept": "application/json",
        }

    async def search_restaurants(
        self, 
        location: Dict[str, float], 
        radius_km: int = None
    ) -> Generator[Dict, None, None]:
        """Search for restaurants using Google Places API"""
        url = f"{self.base_url}/nearbysearch/json"
        radius = min((radius_km or settings.DEFAULT_RADIUS_KM) * 1000, 50000)  # Convert to meters, max 50km
        
        params = {
            "location": f"{location['lat']},{location['lng']}",
            "radius": radius,
            "type": "restaurant",
            "key": self.api_key
        }
        
        try:
            response = await self._make_request(url, params)
            results = response.get("results", [])
            
            for result in results:
                yield {
                    "id": result["place_id"],
                    "name": result["name"],
                    "location": {
                        "lat": result["geometry"]["location"]["lat"],
                        "lng": result["geometry"]["location"]["lng"],
                        "address": result.get("vicinity", "")
                    },
                    "rating": result.get("rating"),
                    "review_count": result.get("user_ratings_total"),
                    "price_level": result.get("price_level")
                }

            # Handle pagination
            next_page_token = response.get("next_page_token")
            while next_page_token:
                await asyncio.sleep(2)  # Required delay for next_page_token to become valid
                params["pagetoken"] = next_page_token
                response = await self._make_request(url, params)
                results = response.get("results", [])
                
                for result in results:
                    yield {
                        "id": result["place_id"],
                        "name": result["name"],
                        "location": {
                            "lat": result["geometry"]["location"]["lat"],
                            "lng": result["geometry"]["location"]["lng"],
                            "address": result.get("vicinity", "")
                        },
                        "rating": result.get("rating"),
                        "review_count": result.get("user_ratings_total"),
                        "price_level": result.get("price_level")
                    }
                
                next_page_token = response.get("next_page_token")
                
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            raise

    async def get_restaurant_details(self, restaurant_id: str) -> Dict:
        """Get detailed information about a restaurant using Place Details API"""
        url = f"{self.base_url}/details/json"
        params = {
            "place_id": restaurant_id,
            "fields": "name,formatted_address,formatted_phone_number,website,"
                     "opening_hours,price_level,rating,reviews,photos,types",
            "key": self.api_key
        }
        
        try:
            response = await self._make_request(url, params)
            result = response["result"]
            
            # Extract and format opening hours
            opening_hours = []
            if "opening_hours" in result and "periods" in result["opening_hours"]:
                for period in result["opening_hours"]["periods"]:
                    if "open" in period and "close" in period:
                        opening_hours.append({
                            "day": period["open"]["day"],
                            "open_time": period["open"]["time"],
                            "close_time": period["close"]["time"],
                            "is_overnight": period["open"]["day"] != period["close"]["day"]
                        })

            # Extract photo references
            photos = []
            if "photos" in result:
                for photo in result["photos"][:5]:  # Limit to 5 photos
                    photo_url = f"{self.base_url}/photo"
                    photo_params = {
                        "maxwidth": 800,
                        "photo_reference": photo["photo_reference"],
                        "key": self.api_key
                    }
                    photos.append(f"{photo_url}?{urlencode(photo_params)}")

            return {
                "formatted_address": result.get("formatted_address"),
                "phone": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "opening_hours": opening_hours,
                "photos": photos,
                "types": result.get("types", []),
                "price_level": result.get("price_level")
            }
            
        except Exception as e:
            logger.error(f"Error getting restaurant details: {str(e)}")
            raise

    async def get_reviews(self, restaurant_id: str) -> List[Dict]:
        """Get reviews for a restaurant"""
        url = f"{self.base_url}/details/json"
        params = {
            "place_id": restaurant_id,
            "fields": "reviews",
            "key": self.api_key
        }
        
        try:
            response = await self._make_request(url, params)
            result = response["result"]
            reviews = result.get("reviews", [])
            
            return [{
                "source": "google",
                "rating": review["rating"],
                "text": review["text"],
                "time": review["time"],
                "author_name": review["author_name"],
                "language": review.get("language", "en")
            } for review in reviews]
            
        except Exception as e:
            logger.error(f"Error getting reviews: {str(e)}")
            raise 