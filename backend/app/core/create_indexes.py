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
        # Analytics: Find associates with is_active=True
        await db["users"].create_index([("role", pymongo.ASCENDING), ("is_active", pymongo.ASCENDING)])

        # Books indexes
        await db["books"].create_index([("is_active", pymongo.ASCENDING)])
        await db["books"].create_index([("categories", pymongo.ASCENDING)])
        await db["books"].create_index([("authors", pymongo.ASCENDING)])
        await db["books"].create_index([("price", pymongo.ASCENDING)])
        # Analytics: Low stock books query
        await db["books"].create_index([
            ("is_active", pymongo.ASCENDING),
            ("stock", pymongo.ASCENDING),
            ("low_stock_threshold", pymongo.ASCENDING)
        ])

        # Projects indexes
        await db["projects"].create_index([("assigned_to", pymongo.ASCENDING)])
        await db["projects"].create_index([("status", pymongo.ASCENDING)])
        await db["projects"].create_index([("created_at", pymongo.DESCENDING)])
        # Analytics: Associate performance lookup (critical for $lookup match)
        await db["projects"].create_index([("assigned_to", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])
        # Analytics: Inactive projects query
        await db["projects"].create_index([("status", pymongo.ASCENDING), ("updated_at", pymongo.ASCENDING)])
        # Analytics: Calculate completion rate and project stats
        await db["projects"].create_index([("created_at", pymongo.ASCENDING), ("updated_at", pymongo.ASCENDING)])

        # Project Requests indexes
        await db["project_requests"].create_index([("customer_id", pymongo.ASCENDING)])
        await db["project_requests"].create_index([("status", pymongo.ASCENDING)])
        await db["project_requests"].create_index([("created_at", pymongo.DESCENDING)])
        # Analytics: Stale requests query
        await db["project_requests"].create_index([
            ("status", pymongo.ASCENDING),
            ("created_at", pymongo.ASCENDING)
        ])

        # Project Updates indexes
        await db["project_updates"].create_index([("project_id", pymongo.ASCENDING)])
        await db["project_updates"].create_index([("created_at", pymongo.DESCENDING)])

        # Reviews indexes
        # Analytics: Average rating calculation
        await db["reviews"].create_index([("rating", pymongo.ASCENDING)])
        # Analytics: Reviews this month query
        await db["reviews"].create_index([("created_at", pymongo.ASCENDING)])

        # Error Logs indexes
        # Analytics: Errors in last 24h query
        await db["error_logs"].create_index([("created_at", pymongo.ASCENDING)])

        # Orders indexes
        await db["orders"].create_index([("customer_id", pymongo.ASCENDING)])
        await db["orders"].create_index([("status", pymongo.ASCENDING)])
        await db["orders"].create_index([("created_at", pymongo.DESCENDING)])
        # Analytics: Order status tracking and filtering
        await db["orders"].create_index([("status", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
        # Analytics: Customer order history query
        await db["orders"].create_index([("customer_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])

        # OTP indexes
        # TTL index — MongoDB auto-deletes expired OTPs (expires_at + 0s grace)
        await db["otps"].create_index(
            [("expires_at", pymongo.ASCENDING)],
            expireAfterSeconds=0,
            name="otp_ttl"
        )
        # Lookup by email + purpose + used — used in every verify call
        await db["otps"].create_index([
            ("email", pymongo.ASCENDING),
            ("purpose", pymongo.ASCENDING),
            ("used", pymongo.ASCENDING),
            ("expires_at", pymongo.DESCENDING),
        ])
        # Rate limit check — count sends per email per hour
        await db["otps"].create_index([
            ("email", pymongo.ASCENDING),
            ("purpose", pymongo.ASCENDING),
            ("created_at", pymongo.DESCENDING),
        ])

        logger.info("✓ MongoDB indexes created successfully.")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise e