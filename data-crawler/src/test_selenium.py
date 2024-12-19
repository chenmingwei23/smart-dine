import sys
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('selenium_test.log')
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting Selenium test...")

try:
    logger.info("Setting up Chrome options...")
    options = Options()
    options.add_argument("--headless=new")
    
    logger.info("Installing ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    logger.info(f"ChromeDriver path: {driver_path}")
    
    logger.info("Creating Chrome service...")
    service = Service(executable_path=driver_path)
    
    logger.info("Starting Chrome...")
    driver = webdriver.Chrome(service=service, options=options)
    
    logger.info("Navigating to Google...")
    driver.get("https://www.google.com")
    
    logger.info(f"Page title: {driver.title}")
    
    logger.info("Test successful!")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    
finally:
    try:
        driver.quit()
        logger.info("Chrome closed successfully")
    except:
        pass

# Also write a simple marker file to confirm the script ran
with open('test_complete.txt', 'w') as f:
    f.write('Test completed')