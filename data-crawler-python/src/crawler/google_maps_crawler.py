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

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Import the content of your existing googlemaps.py here
# The content will be the same, just better organized 