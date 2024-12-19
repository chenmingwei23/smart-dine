import json
import logging
import time
import os
import platform
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
OUTPUT_DIR = "output"
TEST_LOCATION = {
    "address": "19 Dunkeyley Pl, Waterloo, NSW",
    "latitude": -33.899109,
    "longitude": 151.209469
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crawler.log')
    ]
)
logger = logging.getLogger(__name__)

# Print startup message
print("Starting Google Maps Crawler...")
logger.info("Logger initialized")

class SeleniumGoogleMapsCrawler:
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        self.wait = None
        self.setup_driver()

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        try:
            logger.info("Initializing Chrome options...")
            options = Options()
            options.add_argument("--headless=new")  # Updated headless argument
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--lang=en-US")
            options.add_argument("--window-size=1920,1080")
            
            # Additional Windows-specific options
            if platform.system() == 'Windows':
                logger.info("Configuring Windows-specific options...")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-software-rasterizer")
            
            logger.info("Setting up ChromeDriver...")
            try:
                # Use ChromeDriverManager to get the appropriate driver
                driver_path = ChromeDriverManager().install()
                # Fix the path to use the actual chromedriver.exe
                driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
                logger.info(f"ChromeDriver path: {driver_path}")
                
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("ChromeDriver initialized successfully")
                
            except Exception as driver_error:
                logger.error(f"Failed to initialize ChromeDriver: {str(driver_error)}")
                raise
            
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("WebDriverWait configured with 10 second timeout")
            
            # Test the driver
            try:
                logger.info("Testing ChromeDriver with a simple request...")
                self.driver.get("https://www.google.com")
                logger.info("ChromeDriver test successful")
            except Exception as test_error:
                logger.error(f"ChromeDriver test failed: {str(test_error)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in setup_driver: {str(e)}")
            if hasattr(self, 'driver') and self.driver:
                logger.info("Cleaning up failed driver instance")
                self.driver.quit()
            raise

    def search_places(self, query, location):
        """Search for places using Google Maps with Selenium."""
        try:
            # Construct the search URL with coordinates for more precise results
            base_url = f"https://www.google.com/maps/search/{query}/@{location['latitude']},{location['longitude']},15z"
            logger.info(f"Searching at URL: {base_url}")
            
            self.driver.get(base_url)
            time.sleep(3)  # Initial wait for page load
            
            # Wait for the results container
            results_selector = "div.ecceSd"  # Main results container class
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, results_selector)))
            
            # Scroll to load more results
            self._scroll_results()
            
            # Extract and return results
            results = self._extract_places_info(query)
            return results
            
        except TimeoutException:
            logger.error("Timeout waiting for results to load")
            return []
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []

    def _scroll_results(self):
        """Scroll through results to load more places."""
        try:
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "div.ecceSd")
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            
            scroll_attempts = 0
            max_attempts = 10
            
            while scroll_attempts < max_attempts:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
                time.sleep(2)
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
            logger.info(f"Scrolled {scroll_attempts} times to load more results")
                
        except Exception as e:
            logger.error(f"Error while scrolling: {str(e)}")

    def _extract_places_info(self, query):
        """Extract information from loaded place cards."""
        results = []
        try:
            # Wait for place listings to be present
            place_listings = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.Nv2PK")))  # Updated selector for place cards
            
            logger.info(f"Found {len(place_listings)} place listings")
            
            for listing in place_listings:
                try:
                    # Extract basic information
                    place_info = {}
                    
                    # Get name
                    try:
                        name_elem = listing.find_element(By.CSS_SELECTOR, "div.qBF1Pd")
                        place_info['name'] = name_elem.text.strip()
                    except NoSuchElementException:
                        continue  # Skip if no name found
                    
                    # Get rating
                    try:
                        rating_elem = listing.find_element(By.CSS_SELECTOR, "span.MW4etd")
                        place_info['rating'] = float(rating_elem.text.strip())
                    except (NoSuchElementException, ValueError):
                        place_info['rating'] = None
                    
                    # Get review count
                    try:
                        reviews_elem = listing.find_element(By.CSS_SELECTOR, "span.UY7F9")
                        reviews_text = reviews_elem.text.strip("()")
                        place_info['review_count'] = int(reviews_text.replace(",", ""))
                    except (NoSuchElementException, ValueError):
                        place_info['review_count'] = None
                    
                    # Get address
                    try:
                        address_elem = listing.find_element(By.CSS_SELECTOR, "div.W4Efsd:last-child > div.W4Efsd:nth-of-type(1)")
                        place_info['address'] = address_elem.text.strip()
                    except NoSuchElementException:
                        place_info['address'] = None
                    
                    # Get additional details (like hours, type, etc.)
                    try:
                        details_elem = listing.find_element(By.CSS_SELECTOR, "div.W4Efsd:last-child > div.W4Efsd:nth-of-type(2)")
                        place_info['details'] = details_elem.text.strip()
                    except NoSuchElementException:
                        place_info['details'] = None
                    
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
            self._save_results(results, query)
            return results
            
        except Exception as e:
            logger.error(f"Error extracting places info: {str(e)}")
            return []

    def _save_results(self, results, query):
        """Save the extracted results to a JSON file."""
        if results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_dir / f"places_{query}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(results)} results to {filename}")

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

    def __del__(self):
        """Clean up the WebDriver when done."""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    crawler = SeleniumGoogleMapsCrawler()
    crawler.run_test_crawl() 