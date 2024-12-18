from typing import List, Dict, Any
import openai
from ..config import settings
from ..models.restaurant import Restaurant, RestaurantAttributes
import logging
import json

logger = logging.getLogger(__name__)

class RestaurantLabeler:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.system_prompt = """
        You are an expert restaurant analyst. Your task is to analyze restaurant data and reviews 
        to extract specific attributes and characteristics. Be objective and base your analysis 
        on the provided data only. Provide confidence scores (0-1) for each attribute.
        """

    async def analyze_reviews(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Analyze reviews to extract insights about the restaurant"""
        review_texts = [review["text"] for review in reviews]
        combined_text = "\n".join(review_texts[:10])  # Analyze up to 10 reviews
        
        prompt = f"""
        Based on these restaurant reviews, analyze and extract the following attributes:
        - Service speed (fast/medium/slow)
        - Ambiance description
        - Noise level (quiet/moderate/loud)
        - Popular dishes
        - Peak hours
        - Typical wait times
        - Special dietary options available
        
        Reviews:
        {combined_text}
        
        Provide the analysis in JSON format with confidence scores.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing reviews: {str(e)}")
            return {}

    async def categorize_cuisine(self, restaurant_data: Dict) -> List[str]:
        """Determine cuisine types based on restaurant data"""
        menu_items = restaurant_data.get("popular_dishes", [])
        categories = restaurant_data.get("categories", [])
        
        prompt = f"""
        Determine the cuisine types for this restaurant based on the following information:
        Categories: {categories}
        Popular Dishes: {menu_items}
        
        Provide up to 3 cuisine types in JSON array format.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            cuisine_types = json.loads(response.choices[0].message.content)
            return cuisine_types
            
        except Exception as e:
            logger.error(f"Error categorizing cuisine: {str(e)}")
            return []

    async def extract_attributes(self, restaurant: Restaurant) -> RestaurantAttributes:
        """Extract and analyze all restaurant attributes"""
        try:
            # Analyze reviews
            review_analysis = await self.analyze_reviews(restaurant.reviews)
            
            # Categorize cuisine
            cuisine_types = await self.categorize_cuisine({
                "categories": restaurant.raw_data.get("categories", []),
                "popular_dishes": review_analysis.get("popular_dishes", [])
            })
            
            # Combine all attributes
            attributes = RestaurantAttributes(
                cuisine_type=cuisine_types,
                price_level=restaurant.raw_data.get("price_level", 2),
                service_speed=review_analysis.get("service_speed", {}).get("value"),
                ambiance=review_analysis.get("ambiance", {}).get("descriptions", []),
                noise_level=review_analysis.get("noise_level", {}).get("value"),
                parking_availability=review_analysis.get("parking", {}).get("value"),
                dietary_options=review_analysis.get("dietary_options", []),
                popular_dishes=review_analysis.get("popular_dishes", []),
                peak_hours=review_analysis.get("peak_hours", {}),
                wait_time=review_analysis.get("wait_times", {})
            )
            
            return attributes
            
        except Exception as e:
            logger.error(f"Error extracting attributes: {str(e)}")
            raise

    def get_confidence_scores(self, attributes: RestaurantAttributes) -> Dict[str, float]:
        """Calculate confidence scores for extracted attributes"""
        scores = {}
        for field, value in attributes.dict().items():
            if isinstance(value, list):
                scores[field] = 1.0 if value else 0.0
            elif isinstance(value, dict):
                scores[field] = 1.0 if any(value.values()) else 0.0
            else:
                scores[field] = 1.0 if value is not None else 0.0
        return scores 