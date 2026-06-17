"""Observability tools — 7 tools. Calls the backend over HTTP instead of MongoDB."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool, format_error, _serialize
from parkash_mcp.http import ApiError
from parkash_mcp.config import get_base_url


def register_observability_tools(mcp) -> None:

    @mcp.tool()
    async def ping() -> str:
        """
        Check MCP server health and backend connectivity.
        Returns server status, app name, environment, and database connectivity
        as reported by the backend's public /health endpoint.
        """
        try:
            data = await get_client().get("/health")
            data = dict(data or {})
            data["architecture"] = f"MCP → HTTPS → {get_base_url()}"
            return _serialize(data)
        except ApiError as e:
            return format_error(e)

    @mcp.tool()
    async def get_analytics() -> str:
        """
        Get the full operational analytics dashboard.
        Includes: executive summary, revenue stats, top books, associate performance,
        review metrics, low stock alerts, stale requests, and inactive projects.
        Best used to answer: 'How is the store performing?' or 'What needs attention?'
        """
        return await run_tool(get_client().get, "/analytics")

    @mcp.tool()
    async def get_metrics_summary() -> str:
        """
        Get aggregated metric counters — logins, orders, new users, books added, etc.
        Returns current totals and a comparison to the previous period.
        """
        return await run_tool(get_client().get, "/metrics/summary")

    @mcp.tool()
    async def get_metrics_trend() -> str:
        """
        Get 30-day hourly metric trend data suitable for charting.
        Use this to identify patterns in user activity, orders, or errors over time.
        """
        return await run_tool(get_client().get, "/metrics/trend")

    @mcp.tool()
    async def get_audit_logs(
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> str:
        """
        Get the permanent audit log of all important actions across the system.
        Args:
            action: Filter by action type e.g. 'book_created', 'order_placed', 'user_deactivated'.
            actor_id: Filter by actor user ID.
            entity_type: Filter by entity type e.g. 'book', 'order', 'project', 'user'.
            from_date: ISO 8601 datetime string to filter logs after e.g. '2026-01-01T00:00:00Z'.
            page: Page number (default 1).
            page_size: Results per page (default 50).
        """
        params = {
            "page": page, "page_size": page_size,
            "action": action, "actor_id": actor_id,
            "entity_type": entity_type, "from_date": from_date,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await run_tool(get_client().get, "/audit-logs", params=params)

    @mcp.tool()
    async def get_entity_audit_logs(entity_type: str, entity_id: str) -> str:
        """
        Get the full audit trail for a specific entity.
        Args:
            entity_type: Type of entity — 'book', 'order', 'project', 'user', 'review'.
            entity_id: MongoDB ObjectId string of the entity.
        """
        return await run_tool(
            get_client().get, f"/audit-logs/entity/{entity_type}/{entity_id}"
        )

    @mcp.tool()
    async def get_error_logs(
        level: Optional[str] = None,
        endpoint: Optional[str] = None,
        from_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> str:
        """
        Get recent error logs (last 7 days — older logs auto-deleted by MongoDB TTL).
        Args:
            level: Filter by severity — 'ERROR', 'WARNING', 'CRITICAL'.
            endpoint: Filter by API endpoint path e.g. '/auth/login'.
            from_date: ISO 8601 datetime string to filter logs after.
            page: Page number (default 1).
            page_size: Results per page (default 50).
        """
        params = {
            "page": page, "page_size": page_size,
            "level": level, "endpoint": endpoint, "from_date": from_date,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await run_tool(get_client().get, "/error-logs", params=params)
