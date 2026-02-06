"""
Mongo client helpers with lazy singleton initialization.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.settings import settings


_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get mongo client.

    :return: TODO - describe return value.
    :rtype: AsyncIOMotorClient
    :raises Exception: If the operation fails.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.mongo.uri)
    return _mongo_client


def get_mongo_database() -> AsyncIOMotorDatabase:
    """
    Get mongo database.

    :return: TODO - describe return value.
    :rtype: AsyncIOMotorDatabase
    :raises Exception: If the operation fails.
    """
    return get_mongo_client()[settings.mongo.db]


async def close_mongo_client() -> None:
    """
    Close mongo client.

    :return: None.
    :raises Exception: If the operation fails.
    """
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
