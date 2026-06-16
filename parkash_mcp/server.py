"""
Parkash Book Depot — MCP Server

32 tools across 6 domains. Architecture: MCP → Services → MongoDB (no HTTP).

Running:
    cd Parkash-Book-Depot
    python -m parkash_mcp.server

Claude Desktop (~/.claude/claude_desktop_config.json):
{
  "mcpServers": {
    "parkash-book-depot": {
      "command": "python",
      "args": ["-m", "parkash_mcp.server"],
      "cwd": "/path/to/Parkash-Book-Depot",
      "env": {
        "MONGODB_URL": "...",
        "MONGODB_DB_NAME": "parkash_book_depot",
        "SECRET_KEY": "...", "PEPPER": "...",
        "CLOUDINARY_CLOUD_NAME": "...", "CLOUDINARY_API_KEY": "...", "CLOUDINARY_API_SECRET": "...",
        "RESEND_API_KEY": "...", "EMAIL_FROM": "...",
        "GOOGLE_CLIENT_ID": "...", "GOOGLE_CLIENT_SECRET": "..."
      }
    }
  }
}
"""

from __future__ import annotations
import sys
import os
import asyncio
import logging

# Ensure backend/ is on the path so `app.*` imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from mcp.server.fastmcp import FastMCP
from parkash_mcp.context import startup, shutdown
from parkash_mcp.tools.books import register_book_tools
from parkash_mcp.tools.orders import register_order_tools
from parkash_mcp.tools.users import register_user_tools
from parkash_mcp.tools.projects import register_project_tools
from parkash_mcp.tools.reviews import register_review_tools
from parkash_mcp.tools.observability import register_observability_tools

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="Parkash Book Depot",
    instructions=(
        "You have admin-level access to the Parkash Book Depot management system. "
        "All data comes directly from MongoDB — no HTTP round-trips. "
        "All write actions are audit-logged under 'MCP Server' identity. "
        "Use read tools freely. For destructive tools (delete_review), "
        "confirm=True is required. Never attempt to place or cancel customer orders — "
        "those are customer-only actions not available here."
    ),
)

# Register all tools
register_book_tools(mcp)
register_order_tools(mcp)
register_user_tools(mcp)
register_project_tools(mcp)
register_review_tools(mcp)
register_observability_tools(mcp)


async def _run() -> None:
    await startup()
    logger.info("MCP Server: MongoDB connected — 32 tools ready")
    try:
        await mcp.run_async()
    finally:
        await shutdown()
        logger.info("MCP Server: shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(_run())