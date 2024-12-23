# -*- coding: utf-8 -*-
"""
Google Maps crawler implementation.
Handles the web scraping logic for Google Maps restaurants.
"""

import logging
import re
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 40

logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    def __init__(self, debug=False):
        self.debug = debug
        logger.info(f"Initializing Google Maps scraper (debug mode: {debug})")
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            logger.error(f"Error in scraper: {exc_type.__name__}: {str(exc_value)}")
            traceback.print_exception(exc_type, exc_value, tb)
        logger.info("Closing Chrome driver")
        self.driver.close()
        self.driver.quit()
        return True

    def __get_driver(self):
        logger.info("Setting up Chrome driver")
        options = Options()
        if not self.debug:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("Chrome driver initialized successfully")
        return driver

    def __get_logger(self):
        logger = logging.getLogger('googlemaps_scraper')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

    def sort_by(self, url: str, ind: int) -> int:
        logger.info(f"Sorting results at URL: {url}")
        self.driver.get(url)
        self.__click_on_cookie_agreement()

        wait = WebDriverWait(self.driver, MAX_WAIT)
        tries = 0
        while tries < MAX_RETRY:
            try:
                menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
                menu_bt.click()
                time.sleep(3)
                recent_rating_bt = self.driver.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[ind]
                recent_rating_bt.click()
                time.sleep(5)
                logger.info("Successfully sorted results")
                return 0
            except Exception as e:
                tries += 1
                logger.warning(f'Failed to click sorting button (attempt {tries}/{MAX_RETRY}): {str(e)}')
        return -1

    def get_reviews(self, offset: int) -> List[Dict]:
        """Get reviews starting from the given offset."""
        self.__scroll()
        time.sleep(4)
        self.__expand_reviews()

        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        rblock = response.find_all('div', class_='jftiEf fontBodyMedium')
        parsed_reviews = []
        
        for index, review in enumerate(rblock):
            if index >= offset:
                r = self.__parse_review(review)
                if r:
                    parsed_reviews.append(r)

        logger.info(f"Parsed {len(parsed_reviews)} reviews")
        return parsed_reviews

    def get_account(self, url: str) -> Dict:
        """Get restaurant details from URL."""
        logger.info(f"Fetching restaurant details from URL: {url}")
        self.driver.get(url)
        self.__click_on_cookie_agreement()
        
        try:
            wait = WebDriverWait(self.driver, MAX_WAIT)
            logger.info("Waiting for restaurant name element to load")
            name_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'DUwDvf'))
            )
            restaurant_name = name_element.text.strip()
            logger.info(f"Found restaurant name in page: {restaurant_name}")
            
            # Get the page source after JavaScript has rendered
            logger.info("Getting page source for parsing")
            response = BeautifulSoup(self.driver.page_source, 'html.parser')
            result = self.__parse_place(response, url)
            logger.info(f"Parsed restaurant data: {result.get('restaurant', {}).get('name')}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting restaurant details: {str(e)}", exc_info=True)
            return {'restaurant': {'url': url}, 'reviews': []}

    def __parse_review(self, review_div: BeautifulSoup, restaurant_id: str = None) -> Dict:
        """Parse a single review."""
        review = {}
        
        try:
            if restaurant_id:
                review['restaurant_id'] = restaurant_id
            
            review_id = review_div.get('data-review-id')
            if review_id and restaurant_id:
                review['_id'] = f"{restaurant_id}_review_{review_id}"
                review['id_review'] = review['_id']  # Set id_review to match _id
            else:
                return None  # Skip reviews without valid IDs
            
            text_div = review_div.find('span', class_='wiI7pd')
            if text_div:
                review['text'] = text_div.text.strip()
            else:
                review['text'] = ''

            date_span = review_div.find('span', class_='rsqaWe')
            if date_span:
                review['date'] = date_span.text.strip()

            rating_span = review_div.find('span', class_='kvMYJc')
            if rating_span:
                aria_label = rating_span.get('aria-label', '')
                rating_match = re.search(r'(\d+)', aria_label)
                if rating_match:
                    review['rating'] = int(rating_match.group(1))

            reviewer_div = review_div.find('div', class_='d4r55')
            if reviewer_div:
                review['reviewer'] = {
                    'name': reviewer_div.text.strip(),
                    'total_reviews': None
                }

                stats_div = review_div.find('div', class_='RfnDt')
                if stats_div:
                    stats_text = stats_div.text.strip()
                    reviews_match = re.search(r'(\d+)\s*reviews?', stats_text)
                    if reviews_match:
                        review['reviewer']['total_reviews'] = int(reviews_match.group(1))

        except Exception as e:
            return None

        fields_to_keep = ['_id', 'id_review', 'restaurant_id', 'text', 'date', 'rating', 'reviewer']
        return {k: v for k, v in review.items() if k in fields_to_keep and v is not None}

    def __generate_unique_key(self, name: str, postal_code: str = None) -> str:
        """Generate a unique key from restaurant name and postal code."""
        # Clean the name: lowercase, remove special chars, replace spaces with underscores
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower()).strip()
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        if postal_code:
            # Clean the postal code: remove spaces and special characters
            clean_postal = re.sub(r'[^a-zA-Z0-9]', '', postal_code)
            return f"{clean_name}_{clean_postal}"
        
        return clean_name

    def __parse_place(self, response, url: str) -> Dict:
        """Parse restaurant details from the page."""
        place = {
            'url': url,
            'location': {
                'type': 'Point',
                'coordinates': [],  # Will be populated with [lng, lat] if available
                'address': None,
                'postal_code': None,
                'city': None,
                'state': None,
                'country': None
            },
            'attributes': {},
            'opening_hours': [],
            'photos': []
        }
        reviews = []
        
        try:
            # Parse restaurant name - try multiple selectors
            name = None
            name_selectors = [
                ('h1', 'DUwDvf'),  # Primary selector
                ('h1', 'fontHeadlineLarge'),  # Alternative class
                ('div', 'fontHeadlineLarge'),  # Alternative element
                ('div', 'DUwDvf')  # Fallback
            ]
            
            logger.info("Attempting to find restaurant name using selectors")
            for element, class_name in name_selectors:
                name_element = response.find(element, class_=class_name)
                if name_element and name_element.text.strip():
                    name = name_element.text.strip()
                    logger.info(f"Found restaurant name '{name}' using {element}.{class_name}")
                    break
                else:
                    logger.debug(f"No name found with {element}.{class_name}")
            
            if not name:
                logger.error("Could not find restaurant name with any selector")
                return {'restaurant': place, 'reviews': []}
            
            place['name'] = name
            # Generate a unique ID for the restaurant
            place['_id'] = self.__generate_unique_key(place['name'])
            logger.info(f"Generated ID '{place['_id']}' for restaurant '{place['name']}'")

            # Parse address and location details
            address_element = response.find('button', {'data-item-id': 'address'})
            if address_element:
                # Clean the address text by removing special characters
                address = re.sub(r'[^\x00-\x7F]+', '', address_element.text.strip())
                place['location']['address'] = address
                logger.info(f"Found address: {address}")
                
                # Try to extract postal code from address
                postal_match = re.search(r'\b\d{5}\b', address)
                if postal_match:
                    postal_code = postal_match.group(0)
                    place['location']['postal_code'] = postal_code
                    logger.info(f"Extracted postal code: {postal_code}")
                    # Update ID with postal code if available
                    place['_id'] = self.__generate_unique_key(place['name'], postal_code)
                    logger.info(f"Updated ID with postal code: {place['_id']}")
                
                # Try to parse address components
                address_parts = address.split(',')
                if len(address_parts) >= 3:
                    place['location']['city'] = address_parts[-3].strip()
                    state_zip = address_parts[-2].strip().split()
                    if len(state_zip) >= 1:
                        place['location']['state'] = state_zip[0]
                    place['location']['country'] = address_parts[-1].strip()

            # Try to extract coordinates from URL
            coords_match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
            if coords_match:
                lat = float(coords_match.group(1))
                lng = float(coords_match.group(2))
                place['location']['coordinates'] = [lng, lat]  # GeoJSON uses [longitude, latitude]
                logger.info(f"Extracted coordinates: {lat}, {lng}")

            # Parse phone number
            phone_button = response.find('button', {'data-item-id': 'phone:tel:'})
            if phone_button:
                place['phone'] = phone_button.text.strip()
                logger.info(f"Found phone number: {place['phone']}")

            # Parse website
            website_button = response.find('a', {'data-item-id': 'authority'})
            if website_button:
                place['website'] = website_button.get('href')
                logger.info(f"Found website: {place['website']}")

            # Parse attributes (price level, cuisine type)
            category_div = response.find('div', class_='skqShb')
            if category_div:
                categories = []
                for span in category_div.find_all('span'):
                    text = re.sub(r'[^\x00-\x7F]+', '', span.text.strip())  # Remove non-ASCII chars
                    if text and not text.startswith('(') and not text.startswith('·'):
                        categories.append(text)
                
                if categories:
                    # First item might be price level
                    if categories[0].startswith('$'):
                        place['attributes']['price_level'] = len(categories[0])
                        place['attributes']['cuisine_type'] = categories[1:]
                    else:
                        place['attributes']['cuisine_type'] = categories

            # Parse reviews
            reviews_container = response.find_all('div', class_='jftiEf fontBodyMedium')
            if reviews_container:
                for review_div in reviews_container:
                    # Skip reviews without a review ID
                    review_id = review_div.get('data-review-id')
                    if not review_id:
                        continue
                        
                    review = {
                        'restaurant_id': place['_id'],
                        'text': self.__get_review_text(review_div),
                        'date': self.__get_review_date(review_div),
                        'rating': self.__get_review_rating(review_div),
                        'reviewer': {
                            'name': self.__get_review_username(review_div),
                            'review_count': self.__get_reviewer_review_count(review_div),
                            'photo_count': self.__get_reviewer_photo_count(review_div),
                            'url': self.__get_reviewer_url(review_div)
                        }
                    }
                    
                    # Only add reviews with text content
                    if not review.get('text'):
                        continue
                        
                    # Generate review ID
                    review['_id'] = f"{place['_id']}_review_{review_id}"
                    review['id_review'] = review['_id']  # Set id_review to match _id
                    reviews.append(review)
                
                # Calculate average rating and review count from reviews
                ratings = [r['rating'] for r in reviews if r.get('rating')]
                if ratings:
                    place['overall_rating'] = sum(ratings) / len(ratings)
                    place['total_reviews'] = len(ratings)

            # Log the final place data before returning
            logger.info(f"Final restaurant data: {place}")
            return {'restaurant': place, 'reviews': reviews}

        except Exception as e:
            logger.error(f"Error parsing restaurant details: {str(e)}", exc_info=True)
            return {'restaurant': place, 'reviews': []}

    def __filter_string(self, str):
        return str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').strip()

    def __click_on_cookie_agreement(self):
        """Click on cookie agreement if present."""
        try:
            agree = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Accept all")]')))
            agree.click()
        except:
            pass

    def __scroll(self):
        """Scroll through reviews."""
        try:
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
            for _ in range(MAX_SCROLLS):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error while scrolling: {str(e)}")

    def __expand_reviews(self):
        """Expand all reviews."""
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
            for button in buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
                except:
                    continue
            return True
        except:
            return False

    def __scroll_page(self, timeout=10, scroll_pause=2):
        """Scroll through the entire page to load all dynamic content."""
        logger.info(f"Scrolling page with timeout {timeout}s")
        start_time = time.time()
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        scroll_count = 0
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_count += 1
            logger.debug(f"Completed scroll {scroll_count}")
            
            # Wait for dynamic content to load
            time.sleep(scroll_pause)
            
            # Try to expand any collapsed sections
            try:
                more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'More')]")
                for button in more_buttons:
                    button.click()
                    time.sleep(0.5)
            except:
                pass

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                logger.info(f"Reached end of page after {scroll_count} scrolls")
                break
            if time.time() - start_time > timeout:
                logger.warning(f"Scroll timeout reached after {scroll_count} scrolls")
                break
                
            last_height = new_height
            logger.debug(f"New height: {new_height}")

    def search_restaurants(self, search_url: str, max_results: int = 20) -> List[str]:
        """Search for restaurants and return their URLs."""
        self.driver.get(search_url)
        self.__click_on_cookie_agreement()
        
        wait = WebDriverWait(self.driver, MAX_WAIT)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Nv2PK')))
        
        urls = []
        scrolls = 0
        
        while len(urls) < max_results and scrolls < MAX_SCROLLS:
            elements = self.driver.find_elements(By.CLASS_NAME, 'Nv2PK')
            
            for element in elements:
                try:
                    link = element.find_element(By.CSS_SELECTOR, 'a.hfpxzc')
                    url = link.get_attribute('href')
                    if url and url not in urls:
                        urls.append(url)
                except:
                    continue
                
                if len(urls) >= max_results:
                    break
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            scrolls += 1
        
        logger.info(f"Found {len(urls)} restaurants")
        return urls[:max_results]

    def __get_review_text(self, review):
        try:
            text_element = review.find('span', class_='wiI7pd')
            if text_element:
                return self.__filter_string(text_element.text)
            return None
        except:
            return None

    def __get_review_date(self, review):
        try:
            date_element = review.find('span', class_='rsqaWe')
            if date_element:
                return date_element.text.strip()
            return None
        except:
            return None

    def __get_review_rating(self, review):
        try:
            rating_element = review.find('span', class_='kvMYJc')
            if rating_element and 'aria-label' in rating_element.attrs:
                rating_text = rating_element['aria-label']
                return float(rating_text.split()[0])
            return None
        except:
            return None

    def __get_review_username(self, review):
        try:
            username_element = review.find('div', class_='d4r55')
            if username_element:
                return username_element.text.strip()
            return None
        except:
            return None

    def __get_reviewer_review_count(self, review):
        try:
            count_element = review.find('div', class_='RfnDt')
            if count_element:
                count_text = count_element.text.strip()
                match = re.search(r'(\d+)\s+reviews?', count_text)
                if match:
                    return int(match.group(1))
            return None
        except:
            return None

    def __get_reviewer_photo_count(self, review):
        try:
            count_element = review.find('div', class_='RfnDt')
            if count_element:
                count_text = count_element.text.strip()
                match = re.search(r'(\d+)\s+photos?', count_text)
                if match:
                    return int(match.group(1))
            return None
        except:
            return None

    def __get_reviewer_url(self, review):
        try:
            url_element = review.find('button', class_='WEBjve')
            if url_element and 'data-href' in url_element.attrs:
                return url_element['data-href']
            return None
        except:
            return None