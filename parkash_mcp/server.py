"""
Parkash Book Depot — MCP Server

33 tools across 6 domains. Architecture: MCP → HTTPS → Backend API → MongoDB.

This server no longer connects to MongoDB directly. Every tool call is an
HTTPS request to the deployed backend, which defaults to the Railway
production deployment:

    https://parkash-book-depot-production.up.railway.app/api/v1

Override the target with PARKASH_API_URL (e.g. for local development against
`http://localhost:8000/api/v1`).

Most tools hit admin-only endpoints, so the server needs credentials for an
admin account. Provide either:
  - PARKASH_ACCESS_TOKEN — an already-issued JWT access token, or
  - PARKASH_ADMIN_EMAIL + PARKASH_ADMIN_PASSWORD — the server logs in lazily
    on first request and caches the resulting access token in memory.

Running:
    python -m parkash_mcp.server

Claude Desktop (~/.claude/claude_desktop_config.json):
{
  "mcpServers": {
    "parkash-book-depot": {
      "command": "python",
      "args": ["-m", "parkash_mcp.server"],
      "cwd": "/path/to/Parkash-Book-Depot",
      "env": {
        "PARKASH_API_URL": "https://parkash-book-depot-production.up.railway.app/api/v1",
        "PARKASH_ADMIN_EMAIL": "...",
        "PARKASH_ADMIN_PASSWORD": "..."
      }
    }
  }
}
"""

from __future__ import annotations
import asyncio
import logging

from mcp.server.fastmcp import FastMCP
from parkash_mcp.config import get_base_url
from parkash_mcp.context import startup, shutdown
from parkash_mcp.tools.books import register_book_tools
from parkash_mcp.tools.orders import register_order_tools
from parkash_mcp.tools.users import register_user_tools
from parkash_mcp.tools.projects import register_project_tools
from parkash_mcp.tools.reviews import register_review_tools
from parkash_mcp.tools.observability import register_observability_tools
from parkash_mcp.tools.health import register_health_tools

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="Parkash Book Depot",
    instructions=(
        "You have admin-level access to the Parkash Book Depot management system. "
        "All data comes from the backend's HTTPS API (no direct database access). "
        "All write actions are audit-logged server-side under the authenticated "
        "admin identity. Use read tools freely. For destructive tools (delete_review), "
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
register_health_tools(mcp)


async def _run() -> None:
    await startup()
    logger.info(f"MCP Server: targeting {get_base_url()} — 33 tools ready")
    try:
        await mcp.run_stdio_async()
    finally:
        await shutdown()
        logger.info("MCP Server: shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(_run())
