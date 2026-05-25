
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

backend_root = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_root))
load_dotenv(backend_root / ".env")

from app.core.database import connect_to_mongo, get_database
from app.core.security import hash_password
from app.core.enums import UserRole
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ── Associate credentials — MUST be set via environment variables ──────────────
ASSOCIATE_NAME     = os.getenv("ASSOCIATE_NAME")
ASSOCIATE_EMAIL    = os.getenv("ASSOCIATE_EMAIL")
ASSOCIATE_PASSWORD = os.getenv("ASSOCIATE_PASSWORD")

# Validate that all required env vars are set
if not ASSOCIATE_NAME or not ASSOCIATE_EMAIL or not ASSOCIATE_PASSWORD:
    logger.error("ERROR: Missing required environment variables.")
    logger.error("Please set: ASSOCIATE_NAME, ASSOCIATE_EMAIL, ASSOCIATE_PASSWORD")
    sys.exit(1)


async def create_associate():
    await connect_to_mongo()
    db = get_database()
    users = db["users"]

    # Check if this associate already exists
    existing = await users.find_one({"email": ASSOCIATE_EMAIL})
    if existing:
        logger.info(f"Associate with email '{ASSOCIATE_EMAIL}' already exists. Nothing to do.")
        return

    # Create the associate document
    associate_doc = {
        "name":            ASSOCIATE_NAME,
        "email":           ASSOCIATE_EMAIL,
        "hashed_password": hash_password(ASSOCIATE_PASSWORD),
        "role":            UserRole.ASSOCIATE.value,
        "is_active":       True,
        "phone":           None,
        "address":         None,
        "created_at":      datetime.now(timezone.utc),
        "updated_at":      datetime.now(timezone.utc),
    }

    await users.insert_one(associate_doc)
    logger.info(f"✓ Associate account created successfully.")
    logger.info(f"  Email:    {ASSOCIATE_EMAIL}")
    logger.info(f"  Password: {ASSOCIATE_PASSWORD}")
    logger.info(f"  → Change this password immediately after first login.")


if __name__ == "__main__":
    asyncio.run(create_associate())