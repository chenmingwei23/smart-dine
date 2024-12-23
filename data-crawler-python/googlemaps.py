# -*- coding: utf-8 -*-
import itertools
import logging
import re
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 40

class GoogleMapsScraper:
    def __init__(self, debug=False):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.driver.close()
        self.driver.quit()
        return True

    def __get_driver(self):
        options = Options()
        if not self.debug:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def __get_logger(self):
        logger = logging.getLogger('googlemaps_scraper')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

    def sort_by(self, url: str, ind: int) -> int:
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
                return 0
            except Exception as e:
                tries += 1
                self.logger.warning('Failed to click sorting button')
        return -1

    def get_reviews(self, offset: int) -> List[Dict]:
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
                    print(r)

        return parsed_reviews

    def get_account(self, url: str) -> Dict:
        self.driver.get(url)
        self.__click_on_cookie_agreement()
        time.sleep(2)

        # Scroll through the page to load all content
        self.__scroll_page()
        
        resp = BeautifulSoup(self.driver.page_source, 'html.parser')
        return self.__parse_place(resp, url)

    def __parse_review(self, review) -> Optional[Dict]:
        try:
            item = {
                'id_review': review.get('data-review-id'),
                'caption': self.__get_review_text(review),
                'relative_date': self.__get_review_date(review),
                'retrieval_date': datetime.now(),
                'rating': self.__get_review_rating(review),
                'username': self.__get_review_username(review),
                'n_review_user': self.__get_reviewer_review_count(review),
                'n_photo_user': self.__get_reviewer_photo_count(review),
                'url_user': self.__get_reviewer_url(review)
            }
            return {k: v for k, v in item.items() if v is not None}
        except Exception as e:
            self.logger.error(f"Error parsing review: {str(e)}")
            return None

    def __parse_place(self, response: BeautifulSoup, url: str) -> Dict:
        place = {
            'name': self.__get_place_name(response),
            'overall_rating': self.__get_place_rating(response),
            'total_reviews': self.__get_total_reviews(response),
            'address': self.__get_address(response),
            'phone': self.__get_phone(response),
            'website': self.__get_website(response),
            'opening_hours': self.__get_opening_hours(response),
            'price_level': self.__get_price_level(response),
            'cuisine_type': self.__get_cuisine_types(response),
            'photos': self.__get_photos(response),
            'coordinates': self.__get_coordinates(response),
            'url': url
        }
        return {k: v for k, v in place.items() if v is not None}

    # Helper methods for parsing place data
    def __get_place_name(self, response):
        try:
            return response.find('h1', class_='DUwDvf fontHeadlineLarge').text.strip()
        except:
            return None

    def __get_place_rating(self, response):
        try:
            rating_text = response.find('div', class_='F7nice').find('span', class_='ceNzKf')['aria-label']
            return float(rating_text.split()[1])
        except:
            return None

    def __get_total_reviews(self, response):
        try:
            reviews_text = response.find('div', class_='F7nice').text
            return int(re.search(r'(\d+) reviews?', reviews_text).group(1))
        except:
            return None

    def __get_address(self, response):
        try:
            address_button = response.find('button', {'data-item-id': 'address'})
            return address_button.text.strip()
        except:
            return None

    def __get_phone(self, response):
        try:
            phone_button = response.find('button', {'data-item-id': 'phone'})
            return phone_button.text.strip()
        except:
            return None

    def __get_website(self, response):
        try:
            website_button = response.find('a', {'data-item-id': 'authority'})
            return website_button['href']
        except:
            return None

    def __get_opening_hours(self, response):
        try:
            hours_div = response.find('div', {'class': 'OqCZI fontBodyMedium'})
            if not hours_div:
                return {}
            
            hours_dict = {}
            days = hours_div.find_all('div', {'class': 'G8aQO'})
            for day in days:
                day_name = day.find('div', {'class': 'y0skZc'}).text.strip()
                hours = day.find('div', {'class': 'G8aQO'}).text.strip()
                hours_dict[day_name] = hours
            return hours_dict
        except:
            return {}

    def __get_price_level(self, response):
        try:
            price_text = response.find('span', string=re.compile(r'^\$+$')).text
            return len(price_text)  # Number of $ symbols
        except:
            return None

    def __get_cuisine_types(self, response):
        try:
            categories = response.find_all('span', {'class': 'DkEaL'})
            return [cat.text.strip() for cat in categories]
        except:
            return []

    def __get_photos(self, response):
        try:
            photo_elements = response.find_all('button', {'class': 'Uf0tqf'})
            return [elem.find('img')['src'] for elem in photo_elements if elem.find('img')]
        except:
            return []

    def __get_coordinates(self, response):
        try:
            url = self.driver.current_url
            coords = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
            if coords:
                return {'lat': float(coords.group(1)), 'lng': float(coords.group(2))}
        except:
            return None

    # Helper methods for parsing reviews
    def __get_review_text(self, review):
        try:
            return self.__filter_string(review.find('span', class_='wiI7pd').text)
        except:
            return None

    def __get_review_date(self, review):
        try:
            return review.find('span', class_='rsqaWe').text
        except:
            return None

    def __get_review_rating(self, review):
        try:
            return float(review.find('span', class_='kvMYJc')['aria-label'].split()[0])
        except:
            return None

    def __get_review_username(self, review):
        try:
            return review['aria-label']
        except:
            return None

    def __get_reviewer_review_count(self, review):
        try:
            return int(review.find('div', class_='RfnDt').text.split()[3])
        except:
            return 0

    def __get_reviewer_photo_count(self, review):
        try:
            photos_text = review.find('div', class_='RfnDt').text
            return int(re.search(r'(\d+) photos?', photos_text).group(1))
        except:
            return 0

    def __get_reviewer_url(self, review):
        try:
            return review.find('button', class_='WEBjve')['data-href']
        except:
            return None

    def __click_on_cookie_agreement(self):
        try:
            agree = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Accept all")]')))
            agree.click()
        except:
            pass

    def __scroll(self):
        scrollable_div = self.driver.find_element(By.XPATH,
            '//div[@class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd"]')
        for _ in range(MAX_SCROLLS):
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(0.1)

    def __scroll_page(self):
        """Scroll the entire page to load all content"""
        for _ in range(3):  # Scroll a few times to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    def __expand_reviews(self):
        try:
            # Click "More" buttons in reviews
            buttons = self.driver.find_elements(By.XPATH, '//button[@class="M77dve"]')
            for button in buttons:
                button.click()
                time.sleep(0.1)
        except:
            pass

    def __filter_string(self, str):
        return str.replace('\r', ' ').replace('\n', ' ').strip()

    def search_restaurants(self, search_url: str, max_results: int = 100) -> List[str]:
        """Search for restaurants in a given area and return their URLs"""
        self.driver.get(search_url)
        self.__click_on_cookie_agreement()
        time.sleep(2)

        restaurant_urls = []
        last_count = 0
        retries = 0

        while len(restaurant_urls) < max_results and retries < 3:
            # Scroll to load more results
            self.__scroll_page()
            
            # Find all restaurant links
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            elements = soup.find_all('a', {'class': 'hfpxzc'})
            
            # Extract URLs
            current_urls = [elem['href'] for elem in elements if elem.get('href')]
            restaurant_urls = list(dict.fromkeys(current_urls))  # Remove duplicates
            
            # Check if we're still finding new restaurants
            if len(restaurant_urls) == last_count:
                retries += 1
            else:
                retries = 0
            last_count = len(restaurant_urls)
            
            self.logger.info(f"Found {len(restaurant_urls)} restaurants")
            
            # Break if we have enough results
            if len(restaurant_urls) >= max_results:
                restaurant_urls = restaurant_urls[:max_results]
                break
                
            time.sleep(2)

        return restaurant_urls
