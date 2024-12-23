"""
Simple MongoDB Atlas connection test.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import ssl

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    try:
        # Get MongoDB URL from environment
        mongo_url = os.getenv("CRAWLER_MONGODB_URL")
        db_name = os.getenv("CRAWLER_MONGODB_DB", "smartdine")
        
        print("Connecting to MongoDB Atlas...")
        print(f"Database: {db_name}")
        
        # Configure MongoDB client
        client = MongoClient(
            mongo_url,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        db = client[db_name]
        db.command("ping")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        print("Connection test successful!")
        client.close()
        
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {str(e)}")
        raise

if __name__ == "__main__":
    test_mongodb_connection() 