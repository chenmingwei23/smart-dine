import json
import logging
import time
import os
import platform
from datetime import datetime
from pathlib import Path
import random

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

    def _get_place_reviews(self, listing):
        """Get reviews for a specific place by clicking on it and extracting review data."""
        try:
            # Click on the listing to open details
            listing.click()
            time.sleep(2)  # Wait for details to load

            # Wait for reviews section
            reviews_section = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.jftiEf")
            ))

            # Click "More reviews" button if available
            try:
                more_reviews_button = self.driver.find_element(By.CSS_SELECTOR, "button.w8nwRe")
                more_reviews_button.click()
                time.sleep(2)  # Wait for more reviews to load
            except NoSuchElementException:
                pass

            # Get all review elements
            review_elements = reviews_section.find_elements(By.CSS_SELECTOR, "div.jJc9Ad")
            reviews = []

            for review in review_elements[:10]:  # Limit to first 10 reviews
                try:
                    review_data = {}
                    
                    # Get reviewer name
                    try:
                        reviewer_elem = review.find_element(By.CSS_SELECTOR, "div.d4r55")
                        review_data['reviewer'] = reviewer_elem.text.strip()
                    except NoSuchElementException:
                        review_data['reviewer'] = None

                    # Get rating
                    try:
                        rating_elem = review.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                        aria_label = rating_elem.get_attribute("aria-label")
                        rating = float(aria_label.split()[0])  # "4.0 stars" -> 4.0
                        review_data['rating'] = rating
                    except (NoSuchElementException, ValueError, AttributeError):
                        review_data['rating'] = None

                    # Get review text
                    try:
                        text_elem = review.find_element(By.CSS_SELECTOR, "span.wiI7pd")
                        review_data['text'] = text_elem.text.strip()
                    except NoSuchElementException:
                        review_data['text'] = None

                    # Get review date
                    try:
                        date_elem = review.find_element(By.CSS_SELECTOR, "span.rsqaWe")
                        review_data['date'] = date_elem.text.strip()
                    except NoSuchElementException:
                        review_data['date'] = None

                    reviews.append(review_data)

                except Exception as e:
                    logger.error(f"Error extracting review data: {str(e)}")
                    continue

            # Go back to results
            try:
                back_button = self.driver.find_element(By.CSS_SELECTOR, "button.VfPpkd-icon-LgbsSe")
                back_button.click()
                time.sleep(1)  # Wait for results to reload
            except NoSuchElementException:
                logger.warning("Back button not found, trying to navigate back")
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(1)

            return reviews

        except Exception as e:
            logger.error(f"Error getting place reviews: {str(e)}")
            return []

    def _get_place_details(self, listing):
        """Get detailed information for a place by clicking on it and extracting all available data."""
        try:
            # Click on the listing to open details
            listing.click()
            time.sleep(2)  # Wait for details to load

            details = {}

            # Get photos with fallback
            try:
                photos_container = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button.gallery-image-container")
                ))
                photo_url = photos_container.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                details['photo_url'] = photo_url
            except Exception as e:
                logger.warning(f"Could not get photo, using fallback: {str(e)}")
                # Fallback to a random restaurant image
                fallback_images = [
                    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                    "https://images.unsplash.com/photo-1552566626-52f8b828add9",
                    "https://images.unsplash.com/photo-1514933651103-005eec06c04b"
                ]
                import random
                details['photo_url'] = random.choice(fallback_images)

            # Get exact location (coordinates) with soft fail
            try:
                current_url = self.driver.current_url
                coords = current_url.split('@')[1].split(',')[:2]
                details['exact_location'] = {
                    'latitude': float(coords[0]),
                    'longitude': float(coords[1])
                }
            except Exception as e:
                logger.warning(f"Could not get exact location: {str(e)}")
                details['exact_location'] = None

            # Get opening hours with soft fail
            try:
                # First try to find and click the hours button with updated selectors
                hours_button_selectors = [
                    "button[jsaction*='pane.openhours.expand']",  # Main hours button
                    "button[aria-label*='opening hours']",  # Alternative by aria-label
                    "button[aria-label*='Hours']",  # Another alternative
                    "div[jsaction*='openhours.expand']"  # Div that might be clickable
                ]

                hours_clicked = False
                for selector in hours_button_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            try:
                                # Check if it's the hours button by its text or aria-label
                                button_text = (button.get_attribute("aria-label") or button.text).lower()
                                if any(keyword in button_text for keyword in ["hour", "open", "time"]):
                                    button.click()
                                    hours_clicked = True
                                    time.sleep(2)  # Wait for hours to load
                                    logger.info("Successfully clicked hours button")
                                    break
                            except:
                                continue
                        if hours_clicked:
                            break
                    except:
                        continue

                if not hours_clicked:
                    logger.warning("Could not find hours button")
                    details['opening_hours'] = None
                    raise Exception("Hours button not found")

                # Try to get the hours from the dialog or expanded section
                opening_hours = {}
                hours_container_selectors = [
                    "table.WgFkxc",  # Main hours table
                    "div[role='dialog'] table",  # Hours in dialog
                    "div.t39EBf.GUrTXd"  # Hours in expanded section
                ]

                hours_found = False
                for container_selector in hours_container_selectors:
                    try:
                        hours_container = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
                        )
                        
                        # Try different row selectors
                        row_selectors = ["tr", "div.G8aQO", "div[role='row']"]
                        for row_selector in row_selectors:
                            rows = hours_container.find_elements(By.CSS_SELECTOR, row_selector)
                            if rows:
                                for row in rows:
                                    try:
                                        # Try different cell selectors for day and time
                                        day_selectors = ["th", "div[role='cell']:first-child", "div.mxowUb"]
                                        time_selectors = ["td", "div[role='cell']:last-child", "div.G8aQO"]
                                        
                                        day = None
                                        time_range = None
                                        
                                        # Get day
                                        for day_selector in day_selectors:
                                            try:
                                                day_elem = row.find_element(By.CSS_SELECTOR, day_selector)
                                                day = day_elem.text.strip()
                                                if day:
                                                    break
                                            except:
                                                continue
                                        
                                        # Get time
                                        for time_selector in time_selectors:
                                            try:
                                                time_elem = row.find_element(By.CSS_SELECTOR, time_selector)
                                                time_range = time_elem.text.strip()
                                                if time_range:
                                                    break
                                            except:
                                                continue
                                        
                                        if day and time_range:
                                            opening_hours[day] = time_range
                                            hours_found = True
                                    except:
                                        continue
                                
                                if hours_found:
                                    break
                        
                        if hours_found:
                            break
                            
                    except:
                        continue

                # Try to close the dialog if it was opened
                try:
                    close_button_selectors = [
                        "button[jsaction*='modal-dialog-close']",
                        "button[aria-label*='Close']",
                        "button.VfPpkd-icon-LgbsSe"
                    ]
                    for selector in close_button_selectors:
                        try:
                            close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            close_button.click()
                            time.sleep(1)
                            break
                        except:
                            continue
                except:
                    pass

                details['opening_hours'] = opening_hours if opening_hours else None
                if opening_hours:
                    logger.info(f"Successfully collected {len(opening_hours)} days of opening hours")
                else:
                    logger.warning("No opening hours found")

            except Exception as e:
                logger.warning(f"Error getting opening hours: {str(e)}")
                details['opening_hours'] = None

            # Get website URL with soft fail
            try:
                website_button = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                details['website'] = website_button.get_attribute("href")
            except Exception as e:
                logger.warning(f"Could not get website URL: {str(e)}")
                details['website'] = None

            # Get phone number with soft fail
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                details['phone'] = phone_button.get_attribute("aria-label").replace("Phone:", "").strip()
            except Exception as e:
                logger.warning(f"Could not get phone number: {str(e)}")
                details['phone'] = None

            # Get reviews with soft fail
            try:
                reviews = []
                logger.info("Starting review collection...")

                # First, find and click the reviews count/link to open the reviews modal
                review_trigger_selectors = [
                    "button[jsaction*='pane.rating.moreReviews']",  # Main reviews trigger
                    "button[jsaction*='reviewChart']",  # Alternative trigger
                    "span[jsaction*='pane.rating.moreReviews']"  # Text-based trigger
                ]

                review_modal_opened = False
                for selector in review_trigger_selectors:
                    try:
                        triggers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for trigger in triggers:
                            try:
                                # Check if element contains review count
                                trigger_text = trigger.text.lower()
                                if 'review' in trigger_text and any(c.isdigit() for c in trigger_text):
                                    logger.info(f"Found reviews trigger with text: {trigger_text}")
                                    trigger.click()
                                    time.sleep(2)  # Short wait for modal
                                    review_modal_opened = True
                                    break
                            except:
                                continue
                        if review_modal_opened:
                            break
                    except:
                        continue

                if not review_modal_opened:
                    logger.warning("Could not open reviews modal")
                    return details

                # Wait for the reviews modal and get the scrollable container
                reviews_container = None
                container_selectors = [
                    "div[role='dialog'] div[jstrack='review-list']",  # Main reviews container
                    "div[role='dialog'] div[jsaction*='reviewSort']",  # Reviews list container
                    "div[role='dialog'] div.DxyBCb[role='region']",   # Reviews region
                    "div[role='dialog'] div.m6QErb"                   # Backup container
                ]

                # Add random delay between 2-4 seconds
                time.sleep(2 + random.random() * 2)

                # First wait for the modal dialog
                try:
                    modal = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
                    )
                    logger.info("Review modal detected")
                    
                    # Simulate human-like pause
                    time.sleep(1 + random.random())
                    
                    # Try to find the reviews section within the modal
                    for selector in container_selectors:
                        try:
                            reviews_container = modal.find_element(By.CSS_SELECTOR, selector)
                            # Verify container has actual review elements
                            review_elements = reviews_container.find_elements(By.CSS_SELECTOR, 
                                "div.jftiEf, div.gws-localreviews__google-review")
                            
                            if review_elements:
                                logger.info(f"Found {len(review_elements)} review elements with selector: {selector}")
                                break
                            else:
                                logger.info(f"Container found but empty with selector: {selector}")
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Modal detection failed: {str(e)}")
                    return details

                if not reviews_container:
                    logger.warning("Could not find valid reviews container")
                    return details

                # Add random mouse movements to seem more human-like
                try:
                    action = webdriver.ActionChains(self.driver)
                    action.move_to_element(reviews_container)
                    action.move_by_offset(random.randint(-10, 10), random.randint(-10, 10))
                    action.perform()
                except Exception as e:
                    logger.debug(f"Mouse movement failed: {str(e)}")

                # Scroll with random delays and checks
                last_height = 0
                scroll_attempts = 0
                max_attempts = 10
                
                while scroll_attempts < max_attempts:
                    try:
                        # Random delay between scrolls (1-3 seconds)
                        time.sleep(1 + random.random() * 2)
                        
                        # Scroll with a random amount
                        scroll_amount = random.randint(300, 500)
                        self.driver.execute_script(
                            f"arguments[0].scrollTop += {scroll_amount}", 
                            reviews_container
                        )
                        
                        # Check new height
                        new_height = self.driver.execute_script(
                            "return arguments[0].scrollHeight", 
                            reviews_container
                        )
                        
                        if new_height == last_height:
                            scroll_attempts += 1
                        else:
                            last_height = new_height
                            scroll_attempts = 0
                            
                        # Try to expand any "More" buttons
                        more_buttons = reviews_container.find_elements(
                            By.CSS_SELECTOR, 
                            "button.w8nwRe"
                        )
                        for button in more_buttons:
                            try:
                                if "more" in button.text.lower():
                                    # Random delay before clicking (0.5-1.5 seconds)
                                    time.sleep(0.5 + random.random())
                                    button.click()
                            except:
                                continue
                                
                    except Exception as e:
                        logger.warning(f"Scroll attempt failed: {str(e)}")
                        scroll_attempts += 1
                        
                    # Break if we've hit the retry limit
                    if scroll_attempts >= 3:
                        break

                # Now extract all visible reviews
                try:
                    review_elements = reviews_container.find_elements(
                        By.CSS_SELECTOR, 
                        "div.jftiEf, div.gws-localreviews__google-review"
                    )
                    logger.info(f"Found {len(review_elements)} review elements to process")

                    for review in review_elements:
                        try:
                            review_data = {
                                'reviewer': None,
                                'rating': None,
                                'text': None,
                                'date': None
                            }

                            # Get reviewer name (updated selector)
                            try:
                                name_elem = review.find_element(By.CSS_SELECTOR, "div.d4r55, div.TSUbDb")
                                review_data['reviewer'] = name_elem.text.strip()
                            except:
                                continue  # Skip if no reviewer name

                            # Get rating (updated selector)
                            try:
                                rating_elem = review.find_element(By.CSS_SELECTOR, "span.kvMYJc, span[role='img']")
                                aria_label = rating_elem.get_attribute("aria-label")
                                if aria_label:
                                    review_data['rating'] = float(aria_label.split()[0])
                            except:
                                pass

                            # Get review text (updated selector)
                            try:
                                text_elem = review.find_element(By.CSS_SELECTOR, "span.wiI7pd, div.MyEned")
                                review_data['text'] = text_elem.text.strip()
                            except:
                                pass

                            # Get date (updated selector)
                            try:
                                date_elem = review.find_element(By.CSS_SELECTOR, "span.rsqaWe, span[class*='dehysf']")
                                review_data['date'] = date_elem.text.strip()
                            except:
                                pass

                            # Only add reviews with at least some valid data
                            if review_data['reviewer'] and any(v for v in review_data.values() if v):
                                reviews.append(review_data)

                        except Exception as e:
                            logger.warning(f"Error extracting review data: {str(e)}")
                            continue

                    logger.info(f"Successfully collected {len(reviews)} reviews")
                    details['reviews'] = reviews

                    # Try to close the modal
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, "button[jsaction*='modal-dialog-close']")
                        close_button.click()
                        time.sleep(1)
                    except:
                        pass

                except Exception as e:
                    logger.warning(f"Error getting reviews: {str(e)}")
                    details['reviews'] = []

            except Exception as e:
                logger.warning(f"Error getting reviews: {str(e)}")
                details['reviews'] = []

            # Go back to results with soft fail
            try:
                try:
                    back_button = self.driver.find_element(By.CSS_SELECTOR, "button.VfPpkd-icon-LgbsSe")
                    back_button.click()
                    time.sleep(1)
                except:
                    logger.warning("Back button not found, trying history.back()")
                    self.driver.execute_script("window.history.go(-1)")
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"Error going back to results: {str(e)}")

            return details

        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return {
                'photo_url': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                'exact_location': None,
                'opening_hours': None,
                'website': None,
                'phone': None,
                'reviews': []
            }

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

                    # Get detailed information
                    logger.info(f"Getting detailed information for {place_info['name']}...")
                    detailed_info = self._get_place_details(listing)
                    
                    # Update place_info with detailed information
                    place_info.update({
                        'photo_url': detailed_info.get('photo_url'),
                        'exact_location': detailed_info.get('exact_location'),
                        'opening_hours': detailed_info.get('opening_hours'),
                        'website': detailed_info.get('website'),
                        'phone': detailed_info.get('phone'),
                        'reviews': detailed_info.get('reviews', [])
                    })
                    
                    logger.info(f"Found {len(place_info['reviews'])} reviews")
                    
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