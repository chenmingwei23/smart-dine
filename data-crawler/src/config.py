import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Test Location
TEST_LOCATION = {
    'address': '19 Dunkeyley Pl, Water, NSW, Australia',
    'latitude': -33.7915,  # You'll need to verify these coordinates
    'longitude': 151.2363,
    'radius': 1000,  # Search radius in meters
}

# Output Configuration
OUTPUT_DIR = 'data/raw'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Crawler Configuration
SEARCH_TYPES = ['restaurant', 'cafe', 'bar']
MAX_RESULTS_PER_SEARCH = 20  # Start small for testing
DELAY_BETWEEN_REQUESTS = 2  # seconds 