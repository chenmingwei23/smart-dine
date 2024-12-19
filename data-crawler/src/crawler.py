import json
import time
import logging
from datetime import datetime
from pathlib import Path
import googlemaps
from .config import (
    GOOGLE_MAPS_API_KEY,
    TEST_LOCATION,
    OUTPUT_DIR,
    SEARCH_TYPES,
    MAX_RESULTS_PER_SEARCH,
    DELAY_BETWEEN_REQUESTS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsCrawler:
    def __init__(self):
        self.client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search_places(self, location, search_type):
        """Search for places of a specific type around a location."""
        try:
            results = self.client.places_nearby(
                location=(location['latitude'], location['longitude']),
                radius=location['radius'],
                type=search_type
            )

            places = results.get('results', [])
            
            # Handle pagination if needed
            while 'next_page_token' in results and len(places) < MAX_RESULTS_PER_SEARCH:
                time.sleep(DELAY_BETWEEN_REQUESTS)  # Wait for next page token to become valid
                results = self.client.places_nearby(
                    location=(location['latitude'], location['longitude']),
                    radius=location['radius'],
                    type=search_type,
                    page_token=results['next_page_token']
                )
                places.extend(results.get('results', []))

            return places[:MAX_RESULTS_PER_SEARCH]

        except Exception as e:
            logger.error(f"Error searching for {search_type}: {str(e)}")
            return []

    def get_place_details(self, place_id):
        """Get detailed information about a specific place."""
        try:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return self.client.place(place_id, fields=[
                'name',
                'formatted_address',
                'geometry',
                'formatted_phone_number',
                'website',
                'rating',
                'user_ratings_total',
                'price_level',
                'opening_hours',
                'reviews'
            ])
        except Exception as e:
            logger.error(f"Error getting details for place {place_id}: {str(e)}")
            return None

    def save_results(self, results, search_type):
        """Save crawled results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"{search_type}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(results)} results to {filename}")

    def run_test_crawl(self):
        """Run a test crawl for the specified location."""
        logger.info(f"Starting test crawl for location: {TEST_LOCATION['address']}")
        
        all_results = []
        
        for search_type in SEARCH_TYPES:
            logger.info(f"Searching for {search_type}s...")
            
            # Search for places
            places = self.search_places(TEST_LOCATION, search_type)
            logger.info(f"Found {len(places)} {search_type}s in initial search")
            
            # Get details for each place
            detailed_results = []
            for place in places:
                place_id = place['place_id']
                logger.info(f"Getting details for {place['name']} ({place_id})")
                
                details = self.get_place_details(place_id)
                if details:
                    detailed_results.append({
                        'basic_info': place,
                        'details': details
                    })
            
            # Save results for this type
            if detailed_results:
                self.save_results(detailed_results, search_type)
                all_results.extend(detailed_results)
        
        logger.info(f"Test crawl completed. Total places found: {len(all_results)}")
        return all_results 