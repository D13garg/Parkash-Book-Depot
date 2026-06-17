"""MCP tool for checking backend API health."""

from __future__ import annotations

from typing import Any
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool


def register_health_tools(mcp: Any) -> None:
    """Register health check tools with the FastMCP instance."""

    @mcp.tool()
    async def health_check() -> str:
        """Check the health of the Parkash Book Depot API and database.

        Returns a string containing status, app name, version, environment,
        and database connectivity, as reported by the backend's /health endpoint.
        """
        return await run_tool(get_client().get, "/health")
