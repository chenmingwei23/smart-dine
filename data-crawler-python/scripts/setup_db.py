"""
MongoDB Atlas Database Setup Script

This script initializes the MongoDB collections and creates necessary indexes
for the SmartDine restaurant data crawler.

Usage:
    python scripts/setup_db.py

The script will:
1. Connect to MongoDB Atlas
2. Create collections if they don't exist
3. Set up indexes for efficient querying
4. Verify the setup
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, GEOSPHERE
import ssl

# Load environment variables
load_dotenv()

def create_collection(db, collection_name: str) -> None:
    """Create a collection if it doesn't exist."""
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection already exists: {collection_name}")

def create_index(collection, index_spec: List or Dict, unique: bool = False) -> None:
    """Create an index on a collection."""
    try:
        index_name = collection.create_index(index_spec, unique=unique)
        print(f"Created index '{index_name}' on {collection.name}")
    except Exception as e:
        print(f"Error creating index on {collection.name}: {str(e)}")
        raise

def setup_database():
    """Set up MongoDB collections and indexes."""
    try:
        # Get MongoDB connection details from environment
        mongo_url = os.getenv("CRAWLER_MONGODB_URL")
        db_name = os.getenv("CRAWLER_MONGODB_DB", "smartdine")
        restaurants_collection = os.getenv("CRAWLER_MONGODB_COLLECTION_RESTAURANTS", "restaurants")
        reviews_collection = os.getenv("CRAWLER_MONGODB_COLLECTION_REVIEWS", "reviews")
        
        print(f"\nConnecting to MongoDB Atlas database: {db_name}")
        
        # Configure MongoDB client
        client = MongoClient(
            mongo_url,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas")
        
        # Get database
        db = client[db_name]
        
        # Create collections
        print("\nSetting up collections...")
        create_collection(db, restaurants_collection)
        create_collection(db, reviews_collection)
        
        # Create indexes for restaurants collection
        print("\nSetting up indexes for restaurants collection...")
        restaurants = db[restaurants_collection]
        create_index(restaurants, "url", unique=True)
        create_index(restaurants, [("location.lat", ASCENDING), ("location.lng", ASCENDING)])
        create_index(restaurants, "cuisine_type")
        create_index(restaurants, "overall_rating")
        
        # Create indexes for reviews collection
        print("\nSetting up indexes for reviews collection...")
        reviews = db[reviews_collection]
        create_index(reviews, "id_review", unique=True)
        create_index(reviews, "restaurant_id")
        
        print("\nDatabase setup completed successfully!")
        
        # Print collection statistics
        print("\nCollection Statistics:")
        for collection_name in [restaurants_collection, reviews_collection]:
            collection = db[collection_name]
            doc_count = collection.count_documents({})
            index_count = len(list(collection.list_indexes()))
            print(f"{collection_name}:")
            print(f"  - Documents: {doc_count}")
            print(f"  - Indexes: {index_count}")
        
        client.close()
        
    except Exception as e:
        print(f"\nError setting up database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 