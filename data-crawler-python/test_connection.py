"""
Test MongoDB Atlas connection.
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

from database.mongodb import MongoDBClient
from config.settings import settings

def test_mongodb_connection():
    try:
        # Initialize MongoDB client
        print("Initializing MongoDB client...")
        client = MongoDBClient()
        
        # Test basic operations
        print(f"Connected to database: {client.db_name}")
        print("Testing basic operations...")
        
        # List collections
        collections = client.db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Count documents in restaurants collection
        restaurant_count = client.restaurants.count_documents({})
        print(f"Number of restaurants in database: {restaurant_count}")
        
        print("Connection test successful!")
        client.close()
        
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {str(e)}")
        raise

if __name__ == "__main__":
    test_mongodb_connection() 