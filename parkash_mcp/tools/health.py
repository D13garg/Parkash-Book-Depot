"""MCP tools for checking API health."""

from __future__ import annotations

from typing import Any
from parkash_mcp.adapter import execute_get


def register_health_tools(mcp: Any) -> None:
    """Register health check tools with the FastMCP instance."""
    
    @mcp.tool()
    async def health_check() -> dict[str, Any]:
        """Check the health of the Parkash Book Depot API and database.
        
        Returns:
            A dict containing status, app name, version, environment, and database connectivity.
        """
        return await execute_get("health")
