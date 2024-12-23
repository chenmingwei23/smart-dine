"""
Clean MongoDB collections script.
This script will remove all documents from the restaurants and reviews collections.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_collections():
    """Clean all documents from restaurants and reviews collections."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get MongoDB connection details
        mongo_url = os.getenv("CRAWLER_MONGODB_URL")
        db_name = os.getenv("CRAWLER_MONGODB_DB", "smartdine")
        restaurants_collection = os.getenv("CRAWLER_MONGODB_COLLECTION_RESTAURANTS", "restaurants")
        reviews_collection = os.getenv("CRAWLER_MONGODB_COLLECTION_REVIEWS", "reviews")
        
        logger.info(f"Connecting to MongoDB database: {db_name}")
        
        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Clean restaurants collection
        result = db[restaurants_collection].delete_many({})
        logger.info(f"Deleted {result.deleted_count} documents from {restaurants_collection} collection")
        
        # Clean reviews collection
        result = db[reviews_collection].delete_many({})
        logger.info(f"Deleted {result.deleted_count} documents from {reviews_collection} collection")
        
        # Drop indexes except _id
        logger.info("Dropping indexes from restaurants collection")
        for index in db[restaurants_collection].list_indexes():
            if index['name'] != '_id_':
                db[restaurants_collection].drop_index(index['name'])
                
        logger.info("Dropping indexes from reviews collection")
        for index in db[reviews_collection].list_indexes():
            if index['name'] != '_id_':
                db[reviews_collection].drop_index(index['name'])
        
        logger.info("Collections cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning collections: {str(e)}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    clean_collections() 