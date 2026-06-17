"""
MCP Context — shared HTTP client lifecycle.

The MCP server now talks to the deployed Parkash Book Depot backend over
HTTPS (PARKASH_API_URL, defaulting to the Railway production deployment)
instead of connecting to MongoDB directly. This module owns the single
shared ApiClient instance used by every tool module.
"""

from __future__ import annotations

from parkash_mcp.http import ApiClient

_client: ApiClient | None = None


async def startup() -> None:
    """Create the shared HTTP client on MCP server startup."""
    global _client
    _client = ApiClient()


async def shutdown() -> None:
    """Close the shared HTTP client on MCP server shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_client() -> ApiClient:
    """Return the shared ApiClient instance (same singleton across tools)."""
    if _client is None:
        raise RuntimeError("MCP context not started — call startup() first.")
    return _client
