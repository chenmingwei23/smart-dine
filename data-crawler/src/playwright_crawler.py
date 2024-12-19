import json
import logging
import time
import os
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
OUTPUT_DIR = "output"
TEST_LOCATION = {
    "address": "Gangnam Station, Seoul, South Korea",
    "latitude": 37.498095,
    "longitude": 127.027610
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlaywrightGoogleMapsCrawler:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.context = None
        self.page = None

    async def setup(self):
        """Set up the Playwright browser."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            self.page = await self.context.new_page()
            logger.info("Playwright browser set up successfully")
        except Exception as e:
            logger.error(f"Error setting up Playwright: {str(e)}")
            raise

    async def search_places(self, query, location):
        """Search for places using Google Maps with Playwright."""
        try:
            # Construct the search URL with coordinates
            base_url = f"https://www.google.com/maps/search/{query}/@{location['latitude']},{location['longitude']},15z"
            logger.info(f"Searching at URL: {base_url}")
            
            # Navigate to the URL
            await self.page.goto(base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Wait for the results container
            await self.page.wait_for_selector("div.ecceSd", timeout=10000)
            
            # Scroll to load more results
            await self._scroll_results()
            
            # Extract and return results
            results = await self._extract_places_info(query)
            return results
            
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []

    async def _scroll_results(self):
        """Scroll through results to load more places."""
        try:
            scrollable_selector = "div.ecceSd"
            scroll_attempts = 0
            max_attempts = 10
            
            while scroll_attempts < max_attempts:
                # Get current height
                current_height = await self.page.evaluate(f"""
                    document.querySelector("{scrollable_selector}").scrollHeight
                """)
                
                # Scroll to bottom
                await self.page.evaluate(f"""
                    document.querySelector("{scrollable_selector}").scrollTo(0, 
                        document.querySelector("{scrollable_selector}").scrollHeight
                    )
                """)
                
                # Wait for possible new content to load
                await asyncio.sleep(2)
                
                # Get new height
                new_height = await self.page.evaluate(f"""
                    document.querySelector("{scrollable_selector}").scrollHeight
                """)
                
                if new_height == current_height:
                    break
                    
                scroll_attempts += 1
                
            logger.info(f"Scrolled {scroll_attempts} times to load more results")
                
        except Exception as e:
            logger.error(f"Error while scrolling: {str(e)}")

    async def _extract_places_info(self, query):
        """Extract information from loaded place cards."""
        results = []
        try:
            # Wait for place listings
            await self.page.wait_for_selector("div.Nv2PK", timeout=5000)
            
            # Get all place elements
            place_elements = await self.page.query_selector_all("div.Nv2PK")
            logger.info(f"Found {len(place_elements)} place listings")
            
            for element in place_elements:
                try:
                    place_info = {}
                    
                    # Get name
                    name_element = await element.query_selector("div.qBF1Pd")
                    if name_element:
                        place_info['name'] = await name_element.text_content()
                    else:
                        continue
                    
                    # Get rating
                    rating_element = await element.query_selector("span.MW4etd")
                    if rating_element:
                        rating_text = await rating_element.text_content()
                        try:
                            place_info['rating'] = float(rating_text.strip())
                        except ValueError:
                            place_info['rating'] = None
                    
                    # Get review count
                    reviews_element = await element.query_selector("span.UY7F9")
                    if reviews_element:
                        reviews_text = await reviews_element.text_content()
                        try:
                            reviews_count = reviews_text.strip("()").replace(",", "")
                            place_info['review_count'] = int(reviews_count)
                        except ValueError:
                            place_info['review_count'] = None
                    
                    # Get address
                    address_element = await element.query_selector("div.W4Efsd:last-child > div.W4Efsd:nth-of-type(1)")
                    if address_element:
                        place_info['address'] = await address_element.text_content()
                    
                    # Get additional details
                    details_element = await element.query_selector("div.W4Efsd:last-child > div.W4Efsd:nth-of-type(2)")
                    if details_element:
                        place_info['details'] = await details_element.text_content()
                    
                    # Add metadata
                    place_info.update({
                        'type': query,
                        'crawled_at': datetime.now().isoformat(),
                        'location': {
                            'latitude': TEST_LOCATION['latitude'],
                            'longitude': TEST_LOCATION['longitude']
                        }
                    })
                    
                    results.append(place_info)
                    logger.info(f"Extracted place: {place_info['name']}")
                    
                except Exception as e:
                    logger.error(f"Error extracting info from place card: {str(e)}")
                    continue
            
            # Save the results
            await self._save_results(results, query)
            return results
            
        except Exception as e:
            logger.error(f"Error extracting places info: {str(e)}")
            return []

    async def _save_results(self, results, query):
        """Save the extracted results to a JSON file."""
        if results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_dir / f"places_{query}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(results)} results to {filename}")

    async def run_test_crawl(self):
        """Run a test crawl for restaurants near the test location."""
        try:
            await self.setup()
            logger.info(f"Starting test crawl for location: {TEST_LOCATION['address']}")
            
            search_terms = ['restaurants', 'cafes', 'bars']
            all_results = []
            
            for term in search_terms:
                logger.info(f"Searching for {term}...")
                results = await self.search_places(term, TEST_LOCATION)
                all_results.extend(results)
                
                # Be nice to Google
                await asyncio.sleep(5)
            
            logger.info(f"Test crawl completed. Total places found: {len(all_results)}")
            return all_results
            
        finally:
            if self.browser:
                await self.browser.close()

async def main():
    crawler = PlaywrightGoogleMapsCrawler()
    await crawler.run_test_crawl()

if __name__ == "__main__":
    asyncio.run(main()) 