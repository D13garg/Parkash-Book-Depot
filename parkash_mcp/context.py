"""
MCP Context — database lifecycle and synthetic MCP identity.

The MCP server connects directly to MongoDB using the same Motor client
as the FastAPI app. No HTTP round-trips. No JWT tokens needed.

All write actions are attributed to MCP_USER in the audit log so every
AI-initiated action is distinguishable from human admin actions.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.database import connect_to_mongo, close_mongo_connection, get_database
from backend.app.core.enums import UserRole
from backend.app.models.user import UserModel


# ── Synthetic MCP actor — used as current_user in all service calls ───────────
MCP_USER = UserModel(
    **{
        "_id": "mcp-server",
        "name": "MCP Server",
        "email": "mcp@internal.parkashbookdepot.com",
        "hashed_password": None,
        "role": UserRole.ADMIN.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
)


async def startup() -> None:
    """Establish MongoDB connection on MCP server startup."""
    await connect_to_mongo()


async def shutdown() -> None:
    """Close MongoDB connection on MCP server shutdown."""
    await close_mongo_connection()


def get_db():
    """Return active MongoDB database instance (same singleton as FastAPI)."""
    return get_database()