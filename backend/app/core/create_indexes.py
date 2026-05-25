import logging
import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes in MongoDB collections."""
    logger.info("Creating MongoDB indexes...")
    try:
        # Users indexes
        await db["users"].create_index([("email", pymongo.ASCENDING)], unique=True)

        # Books indexes
        await db["books"].create_index([("is_active", pymongo.ASCENDING)])
        await db["books"].create_index([("categories", pymongo.ASCENDING)])
        await db["books"].create_index([("authors", pymongo.ASCENDING)])
        await db["books"].create_index([("price", pymongo.ASCENDING)])

        # Projects indexes
        await db["projects"].create_index([("assigned_to", pymongo.ASCENDING)])
        await db["projects"].create_index([("status", pymongo.ASCENDING)])
        await db["projects"].create_index([("created_at", pymongo.DESCENDING)])

        # Project Requests indexes
        await db["project_requests"].create_index([("customer_id", pymongo.ASCENDING)])
        await db["project_requests"].create_index([("status", pymongo.ASCENDING)])
        await db["project_requests"].create_index([("created_at", pymongo.DESCENDING)])

        # Project Updates indexes
        await db["project_updates"].create_index([("project_id", pymongo.ASCENDING)])
        await db["project_updates"].create_index([("created_at", pymongo.DESCENDING)])

        logger.info("✓ MongoDB indexes created successfully.")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise e
