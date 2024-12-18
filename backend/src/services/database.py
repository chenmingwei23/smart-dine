from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    def __init__(self):
        self.MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = "smartdine"

    async def connect_to_database(self):
        if self.client is None:
            self.client = AsyncIOMotorClient(self.MONGODB_URL)
            
    async def close_database_connection(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    @property
    def db(self):
        return self.client[self.db_name]

    @property
    def restaurants(self):
        return self.db.restaurants

    @property
    def users(self):
        return self.db.users

# Create a database instance
database = Database() 