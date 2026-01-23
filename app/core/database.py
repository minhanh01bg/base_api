"""
Database module - MongoDB connection management.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager (singleton pattern)."""
    client: Optional[AsyncIOMotorClient] = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create database connection."""
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.mongodb_db_name]
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")


def get_database():
    """Get database instance."""
    if mongodb.database is None:
        raise RuntimeError(
            "Database not connected. Ensure connect_to_mongo() is called."
        )
    return mongodb.database

