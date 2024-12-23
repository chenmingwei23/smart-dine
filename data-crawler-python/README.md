# Google Maps Restaurant Scraper

A Python-based scraper that collects restaurant data and reviews from Google Maps for a specified area.

## Features

- Area-based restaurant search
- Configurable search parameters and filters
- MongoDB integration for data storage
- Comprehensive restaurant data collection:
  - Basic info (name, rating, reviews)
  - Location details
  - Opening hours
  - Reviews and ratings
  - Photos
  - Additional attributes

## Project Structure

```
data-crawler-python/
├── models/             # Data models
│   └── restaurant.py   # Restaurant and related models
├── dao/               # Data Access Objects
│   └── restaurant_dao.py  # MongoDB integration
├── config.py         # Configuration settings
├── googlemaps.py     # Core scraper implementation
├── scraper.py        # Main script
├── requirements.txt  # Python dependencies
└── README.md
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Chrome and ChromeDriver:
- Download Chrome browser if not installed
- ChromeDriver will be automatically managed by the script

3. Configure MongoDB:
- Install MongoDB
- Update MongoDB connection settings in `config.py` if needed

## Configuration

Edit `config.py` to customize:

1. Search Area:
```python
SEARCH_CONFIG = {
    "area": "San Francisco, CA",  # Your target area
    "radius_km": 5,
    "max_restaurants": 100,
    "max_reviews_per_restaurant": 50,
}
```

2. Filters:
```python
RESTAURANT_FILTERS = {
    "min_rating": 3.5,
    "cuisine_types": [],  # Empty for all cuisines
    "price_levels": [],  # Empty for all price levels
}
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
1. Search for restaurants in the specified area
2. Apply configured filters
3. Collect detailed information for each restaurant
4. Store data in MongoDB
5. Log progress to both console and file

## Data Model

Collected restaurant data includes:
- Basic information (name, rating, etc.)
- Location details (address, coordinates)
- Opening hours
- Reviews and ratings
- Photos
- Additional attributes (cuisine type, price level, etc.)

## Logging

- Console output for real-time progress
- Detailed logs in `scraper.log`
- MongoDB for persistent data storage

## License

This project is licensed under the MIT License - see the LICENSE file for details. 