from typing import Dict, List, Generator
from .base import BaseCrawler
from ..config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class YelpCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.api_key = settings.YELP_API_KEY
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def search_restaurants(
        self, 
        location: Dict[str, float], 
        radius_km: int = None
    ) -> Generator[Dict, None, None]:
        """Search for restaurants using Yelp Fusion API"""
        url = f"{self.base_url}/businesses/search"
        radius = min((radius_km or settings.DEFAULT_RADIUS_KM) * 1000, 40000)  # Convert to meters, max 40km
        
        params = {
            "latitude": location["lat"],
            "longitude": location["lng"],
            "radius": radius,
            "categories": "restaurants",
            "sort_by": "rating",
            "limit": 50
        }
        
        try:
            response = await self._make_request(url, params)
            businesses = response.get("businesses", [])
            total = response.get("total", 0)
            
            for business in businesses:
                yield {
                    "id": business["id"],
                    "name": business["name"],
                    "location": {
                        "lat": business["coordinates"]["latitude"],
                        "lng": business["coordinates"]["longitude"],
                        "address": " ".join(business["location"]["display_address"]),
                        "city": business["location"].get("city", ""),
                        "state": business["location"].get("state", ""),
                        "country": business["location"].get("country", ""),
                        "postal_code": business["location"].get("zip_code", "")
                    },
                    "rating": business.get("rating"),
                    "review_count": business.get("review_count"),
                    "price_level": len(business.get("price", "$")) if "price" in business else None
                }

            # Handle pagination if there are more results
            offset = 50
            while offset < min(total, 1000):  # Yelp limits to 1000 results
                params["offset"] = offset
                await asyncio.sleep(0.25)  # Rate limiting
                response = await self._make_request(url, params)
                businesses = response.get("businesses", [])
                
                for business in businesses:
                    yield {
                        "id": business["id"],
                        "name": business["name"],
                        "location": {
                            "lat": business["coordinates"]["latitude"],
                            "lng": business["coordinates"]["longitude"],
                            "address": " ".join(business["location"]["display_address"]),
                            "city": business["location"].get("city", ""),
                            "state": business["location"].get("state", ""),
                            "country": business["location"].get("country", ""),
                            "postal_code": business["location"].get("zip_code", "")
                        },
                        "rating": business.get("rating"),
                        "review_count": business.get("review_count"),
                        "price_level": len(business.get("price", "$")) if "price" in business else None
                    }
                
                offset += 50
                
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            raise

    async def get_restaurant_details(self, restaurant_id: str) -> Dict:
        """Get detailed information about a restaurant"""
        url = f"{self.base_url}/businesses/{restaurant_id}"
        
        try:
            response = await self._make_request(url)
            
            # Extract hours
            hours = []
            if "hours" in response and len(response["hours"]) > 0:
                for day in response["hours"][0]["open"]:
                    hours.append({
                        "day": day["day"],
                        "open_time": day["start"],
                        "close_time": day["end"],
                        "is_overnight": day["is_overnight"]
                    })

            return {
                "phone": response.get("phone"),
                "website": response.get("url"),  # Yelp page URL
                "opening_hours": hours,
                "photos": response.get("photos", []),
                "price_level": len(response.get("price", "$")) if "price" in response else None,
                "categories": [cat["title"] for cat in response.get("categories", [])],
                "attributes": {
                    "takes_reservations": response.get("takes_reservations"),
                    "delivery": response.get("delivery"),
                    "takeout": response.get("takeout"),
                    "accepts_credit_cards": response.get("accepts_credit_cards")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting restaurant details: {str(e)}")
            raise

    async def get_reviews(self, restaurant_id: str) -> List[Dict]:
        """Get reviews for a restaurant"""
        url = f"{self.base_url}/businesses/{restaurant_id}/reviews"
        
        try:
            response = await self._make_request(url)
            reviews = response.get("reviews", [])
            
            return [{
                "source": "yelp",
                "rating": review["rating"],
                "text": review["text"],
                "time": review["time_created"],
                "user_name": review["user"]["name"],
                "language": "en"  # Yelp API returns English reviews by default
            } for review in reviews]
            
        except Exception as e:
            logger.error(f"Error getting reviews: {str(e)}")
            raise 