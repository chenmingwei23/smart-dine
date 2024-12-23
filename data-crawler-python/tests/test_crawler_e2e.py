import os
import pytest
import logging
from pathlib import Path
from datetime import datetime

from src.crawler.google_maps_crawler import GoogleMapsScraper
from dao.restaurant_dao import RestaurantDAO
from .storage.file_storage import FileStorage
from models.restaurant import Restaurant, Review

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_RESTAURANT_URL = "https://www.google.com/maps/place/Lazy+Bear/@37.7604119,-122.4197156,17z"

@pytest.fixture
def file_storage():
    """Create a file storage instance for testing."""
    test_data_dir = Path(__file__).parent / "data"
    storage = FileStorage(base_dir=str(test_data_dir))
    
    # Clean up any existing test data
    if test_data_dir.exists():
        for file in test_data_dir.rglob("*.json"):
            file.unlink()
    
    return storage

@pytest.fixture
def mongodb():
    """Create a MongoDB instance for testing."""
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    dao = RestaurantDAO(mongo_url=mongo_url, db_name="smartdine_test")
    yield dao
    dao.close()

def test_crawler_e2e(file_storage, mongodb):
    """End-to-end test of the crawler with both storage methods."""
    try:
        with GoogleMapsScraper(debug=False) as scraper:
            # Get restaurant data
            restaurant_data = scraper.get_account(TEST_RESTAURANT_URL)
            
            # Verify basic data structure
            assert restaurant_data is not None
            assert 'name' in restaurant_data
            assert 'location' in restaurant_data
            assert 'reviews' in restaurant_data
            
            # Convert to Restaurant model
            restaurant = Restaurant(
                _id=f"{restaurant_data['name'].lower().replace(' ', '_')}_{restaurant_data['location']['postal_code']}",
                **restaurant_data
            )
            
            # Save to file storage
            file_storage.upsert_restaurant(restaurant.dict(by_alias=True))
            
            # Save to MongoDB
            mongodb.upsert_restaurant(restaurant)
            
            # Verify data was saved in both storages
            saved_file = file_storage.get_restaurant(restaurant.id)
            saved_mongo = mongodb.get_restaurant(restaurant.id)
            
            assert saved_file is not None
            assert saved_mongo is not None
            assert saved_file['name'] == restaurant.name
            assert saved_mongo.name == restaurant.name
            
            # Verify specific fields
            assert saved_mongo.location.postal_code is not None
            assert saved_mongo.overall_rating is not None
            assert saved_mongo.total_reviews is not None
            
            # Verify reviews
            file_reviews = file_storage.get_reviews(restaurant.id)
            assert len(file_reviews) > 0
            
            # Log results
            logger.info(f"Successfully crawled and saved restaurant: {restaurant.name}")
            logger.info(f"Saved {len(restaurant.reviews)} reviews")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise