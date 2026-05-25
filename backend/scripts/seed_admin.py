import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make sure the backend root is on the path
backend_root = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_root))

# Load backend/.env (ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, MONGODB_URL, etc.)
load_dotenv(backend_root / ".env")

from app.core.database import connect_to_mongo, get_database
from app.core.security import hash_password
from app.core.enums import UserRole
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ── Admin credentials — MUST be set via environment variables ──────────────────
ADMIN_NAME     = os.getenv("ADMIN_NAME")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Validate that all required env vars are set
if not ADMIN_NAME or not ADMIN_EMAIL or not ADMIN_PASSWORD:
    logger.error("ERROR: Missing required environment variables.")
    logger.error("Please set: ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD")
    sys.exit(1)


async def seed_admin():
    await connect_to_mongo()
    db = get_database()
    users = db["users"]

    # Check if this admin already exists
    existing = await users.find_one({"email": ADMIN_EMAIL})
    if existing:
        logger.info(f"Admin with email '{ADMIN_EMAIL}' already exists. Nothing to do.")
        return

    # Create the admin document
    admin_doc = {
        "name":            ADMIN_NAME,
        "email":           ADMIN_EMAIL,
        "hashed_password": hash_password(ADMIN_PASSWORD),
        "role":            UserRole.ADMIN.value,
        "is_active":       True,
        "phone":           None,
        "address":         None,
        "created_at":      datetime.now(timezone.utc),
        "updated_at":      datetime.now(timezone.utc),
    }

    await users.insert_one(admin_doc)
    logger.info(f"✓ Admin user created successfully.")
    logger.info(f"  Email:    {ADMIN_EMAIL}")
    logger.info(f"  Password: {ADMIN_PASSWORD}")
    logger.info(f"  → Change this password immediately after first login.")


if __name__ == "__main__":
    asyncio.run(seed_admin())