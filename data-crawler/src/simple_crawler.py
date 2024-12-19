import requests
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from .config import TEST_LOCATION, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGoogleMapsCrawler:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_places(self, query, location):
        """Search for places using Google Maps web interface."""
        base_url = "https://www.google.com/maps/search/"
        search_query = f"{query} near {location['address']}"
        url = f"{base_url}{search_query}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # Save the raw HTML for inspection
                self._save_raw_html(response.text, query)
                return self._extract_basic_info(response.text, query)
            else:
                logger.error(f"Failed to get results: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []

    def _save_raw_html(self, html_content, query):
        """Save raw HTML for debugging."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"raw_{query}_{timestamp}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved raw HTML to {filename}")

    def _extract_basic_info(self, html_content, query):
        """Extract basic information from the HTML response."""
        soup = BeautifulSoup(html_content, 'lxml')
        results = []
        
        # Debug: Print the first 1000 characters of HTML
        logger.debug(f"First 1000 chars of HTML: {html_content[:1000]}")
        
        # Look for elements that might contain place information
        # Google Maps typically loads data dynamically, so we need to look for specific patterns
        place_elements = soup.find_all('div', class_='section-result')  # This is a common class for results
        if not place_elements:
            place_elements = soup.find_all('div', class_='place-result')  # Alternative class
        
        logger.info(f"Found {len(place_elements)} potential place elements for {query}")
        
        for element in place_elements:
            try:
                # Try different possible selectors
                name = None
                address = None
                rating = None
                
                # Try to find name
                name_elem = (
                    element.find('h3') or 
                    element.find('div', class_='section-result-title') or
                    element.find('div', class_='place-name')
                )
                if name_elem:
                    name = name_elem.text.strip()
                
                # Try to find address
                address_elem = (
                    element.find('span', class_='section-result-location') or
                    element.find('div', class_='place-address') or
                    element.find('span', class_='address')
                )
                if address_elem:
                    address = address_elem.text.strip()
                
                # Try to find rating
                rating_elem = element.find('span', class_='rating')
                if rating_elem:
                    rating = rating_elem.text.strip()
                
                if name or address:  # Save if we found at least a name or address
                    place_info = {
                        'name': name,
                        'address': address,
                        'rating': rating,
                        'type': query
                    }
                    results.append(place_info)
                    logger.info(f"Extracted place: {name}")
                
            except Exception as e:
                logger.error(f"Error extracting info from element: {str(e)}")
                continue
        
        # Save the extracted results
        if results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_dir / f"extracted_{query}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(results)} extracted results to {filename}")
        else:
            logger.warning(f"No results could be extracted for {query}")
        
        return results

    def run_test_crawl(self):
        """Run a test crawl for restaurants near the test location."""
        logger.info(f"Starting test crawl for location: {TEST_LOCATION['address']}")
        
        search_terms = ['restaurants', 'cafes', 'bars']
        all_results = []
        
        for term in search_terms:
            logger.info(f"Searching for {term}...")
            results = self.search_places(term, TEST_LOCATION)
            all_results.extend(results)
            
            # Be nice to Google
            time.sleep(5)
        
        logger.info(f"Test crawl completed. Total places found: {len(all_results)}")
        return all_results