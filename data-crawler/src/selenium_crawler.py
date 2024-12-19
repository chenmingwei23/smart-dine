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
                # First try to find and click the hours button
                try:
                    hours_button = self.driver.find_element(By.CSS_SELECTOR, "button[jsaction*='hours']")
                    hours_button.click()
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Could not click hours button: {str(e)}")
                    raise

                # Try to get the hours from the dialog
                try:
                    hours_container = self.wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[role='dialog']")
                    ))
                    hours_list = hours_container.find_elements(By.CSS_SELECTOR, "table tr")
                    
                    opening_hours = {}
                    for hour_row in hours_list:
                        try:
                            day = hour_row.find_element(By.CSS_SELECTOR, "th").text.strip()
                            time_range = hour_row.find_element(By.CSS_SELECTOR, "td").text.strip()
                            opening_hours[day] = time_range
                        except:
                            continue

                    # Try to close the dialog if it was opened
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, "button[jsaction*='modal-dialog-close']")
                        close_button.click()
                        time.sleep(1)
                    except:
                        pass

                    details['opening_hours'] = opening_hours if opening_hours else None
                except Exception as e:
                    logger.warning(f"Could not get hours from dialog: {str(e)}")
                    details['opening_hours'] = None
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

                # Wait for reviews section with longer timeout and different selectors
                reviews_section = None
                reviews_selectors = [
                    "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",  # Main reviews container
                    "div.jftiEf",  # Alternative container
                    "div[jsaction*='reviewSort']",  # Reviews sort container
                    "div[jscontroller*='ReviewsDisplayDialog']",  # Reviews dialog
                    "div.section-layout.section-scrollbox"  # Older layout
                ]

                for selector in reviews_selectors:
                    try:
                        reviews_section = self.wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, selector)
                        ))
                        logger.info(f"Found reviews section with selector: {selector}")
                        break
                    except:
                        continue

                if not reviews_section:
                    logger.warning("Could not find reviews section")
                    raise Exception("Reviews section not found")

                # Try to click "More reviews" button with multiple selectors and attempts
                more_reviews_clicked = False
                more_reviews_selectors = [
                    "button.w8nwRe.kyuRq",
                    "button[jsaction*='reviewChart']",
                    "button[aria-label*='review']",
                    "button.allxGc",
                    "button[jsaction*='pane.reviewChart.moreReviews']"
                ]

                for selector in more_reviews_selectors:
                    try:
                        # Try to find all matching buttons and click each until success
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            try:
                                if "review" in button.text.lower() or "more" in button.text.lower():
                                    button.click()
                                    more_reviews_clicked = True
                                    logger.info(f"Clicked 'More reviews' button with text: {button.text}")
                                    time.sleep(3)
                                    break
                            except:
                                continue
                        if more_reviews_clicked:
                            break
                    except:
                        continue

                if not more_reviews_clicked:
                    logger.warning("Could not click 'More reviews' button")

                # Find and scroll the reviews panel
                reviews_panel = None
                panel_selectors = [
                    "div.m6QErb[role='main']",
                    "div[jsaction*='scroll']",
                    "div.DxyBCb",
                    "div.section-layout.section-scrollbox"
                ]

                for selector in panel_selectors:
                    try:
                        reviews_panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if reviews_panel:
                    last_height = 0
                    scroll_attempts = 0
                    max_scroll_attempts = 20  # Increase scroll attempts
                    no_change_count = 0
                    max_no_change = 3

                    while scroll_attempts < max_scroll_attempts and no_change_count < max_no_change:
                        # Scroll down
                        self.driver.execute_script(
                            "arguments[0].scrollTo(0, arguments[0].scrollHeight);", 
                            reviews_panel
                        )
                        time.sleep(2)

                        # Try to expand all "More" buttons in reviews
                        try:
                            more_buttons = reviews_panel.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
                            for button in more_buttons:
                                try:
                                    if "more" in button.text.lower():
                                        button.click()
                                        time.sleep(0.5)
                                except:
                                    continue
                        except:
                            pass

                        # Calculate new scroll height
                        new_height = self.driver.execute_script(
                            "return arguments[0].scrollHeight", 
                            reviews_panel
                        )

                        if new_height == last_height:
                            no_change_count += 1
                        else:
                            no_change_count = 0

                        last_height = new_height
                        scroll_attempts += 1
                        logger.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")

                # Get all review elements with multiple selectors
                review_elements = []
                review_selectors = [
                    "div.jftiEf.fontBodyMedium",
                    "div.gws-localreviews__google-review",
                    "div[jscontroller*='ReviewsDisplayDialog']",
                    "div.ODSEW-ShBeI",
                    "div[data-review-id]",
                    "div.jxjCjc"
                ]

                for selector in review_selectors:
                    try:
                        elements = reviews_section.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            review_elements = elements
                            logger.info(f"Found {len(elements)} review elements with selector: {selector}")
                            break
                    except:
                        continue

                if not review_elements:
                    logger.warning("No review elements found")
                    raise Exception("No review elements found")

                # Process reviews with improved selectors
                for review in review_elements:
                    try:
                        review_data = {
                            'reviewer': None,
                            'reviewer_photo': None,
                            'rating': None,
                            'text': None,
                            'date': None,
                            'likes': 0
                        }

                        # Get reviewer info with multiple selectors
                        reviewer_selectors = [
                            "div.d4r55", "div.WNxzHc", 
                            "div.TSUbDb", "div.author-name"
                        ]
                        for selector in reviewer_selectors:
                            try:
                                reviewer_elem = review.find_element(By.CSS_SELECTOR, selector)
                                review_data['reviewer'] = reviewer_elem.text.strip()
                                try:
                                    profile_img = reviewer_elem.find_element(
                                        By.CSS_SELECTOR, 
                                        "img.NBa7we, img[jsname], img.reviewer-image"
                                    )
                                    review_data['reviewer_photo'] = profile_img.get_attribute("src")
                                except:
                                    pass
                                break
                            except:
                                continue

                        # Get rating with multiple selectors
                        rating_selectors = [
                            "span.kvMYJc", "span[role='img']",
                            "div.Fam1ne", "span.rating"
                        ]
                        for selector in rating_selectors:
                            try:
                                rating_elem = review.find_element(By.CSS_SELECTOR, selector)
                                aria_label = rating_elem.get_attribute("aria-label")
                                if aria_label and any(c.isdigit() for c in aria_label):
                                    review_data['rating'] = float(aria_label.split()[0])
                                    break
                            except:
                                continue

                        # Get review text with multiple selectors
                        text_selectors = [
                            "span.wiI7pd", "div.Jtu6Td",
                            "div.review-text", "span[jsan*='review-full-text']"
                        ]
                        for selector in text_selectors:
                            try:
                                text_elem = review.find_element(By.CSS_SELECTOR, selector)
                                review_data['text'] = text_elem.text.strip()
                                break
                            except:
                                continue

                        # Get review date with multiple selectors
                        date_selectors = [
                            "span.rsqaWe", "span.dehysf",
                            "span.review-date", "span.review-time"
                        ]
                        for selector in date_selectors:
                            try:
                                date_elem = review.find_element(By.CSS_SELECTOR, selector)
                                review_data['date'] = date_elem.text.strip()
                                break
                            except:
                                continue

                        # Only add reviews that have meaningful data
                        if any(value not in (None, '', 0) for value in review_data.values()):
                            reviews.append(review_data)
                            if len(reviews) % 5 == 0:
                                logger.info(f"Processed {len(reviews)} reviews so far")

                    except Exception as e:
                        logger.warning(f"Error extracting review data: {str(e)}")
                        continue

                logger.info(f"Successfully collected {len(reviews)} reviews")
                details['reviews'] = reviews

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