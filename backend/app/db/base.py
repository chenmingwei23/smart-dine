from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from ..core.config import settings

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB database"""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB]
        
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client is not None:
            cls.client.close()
            cls.client = None

    @classmethod
    def get_db(cls):
        """Get database instance"""
        return cls.db

class BaseDAO:
    """Base DAO class with common MongoDB operations"""
    
    def __init__(self, collection_name: str):
        self.collection = MongoDB.get_db()[collection_name]
    
    async def find_one(self, query: Dict) -> Optional[Dict]:
        """Find a single document"""
        return await self.collection.find_one(query)
    
    async def find_many(self, 
                       query: Dict, 
                       skip: int = 0, 
                       limit: int = 100,
                       sort: Optional[List[tuple]] = None) -> List[Dict]:
        """Find multiple documents with pagination"""
        cursor = self.collection.find(query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)
    
    async def count(self, query: Dict) -> int:
        """Count documents matching query"""
        return await self.collection.count_documents(query)
    
    async def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """Execute an aggregation pipeline"""
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
    
    async def insert_one(self, document: Dict) -> str:
        """Insert a single document"""
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def insert_many(self, documents: List[Dict]) -> List[str]:
        """Insert multiple documents"""
        result = await self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    async def update_one(self, query: Dict, update: Dict) -> int:
        """Update a single document"""
        result = await self.collection.update_one(query, update)
        return result.modified_count
    
    async def delete_one(self, query: Dict) -> int:
        """Delete a single document"""
        result = await self.collection.delete_one(query)
        return result.deleted_count 