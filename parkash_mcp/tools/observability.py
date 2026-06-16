"""Observability tools — 7 tools."""
from __future__ import annotations
from typing import Optional
from datetime import datetime
from parkash_mcp.context import get_db
from parkash_mcp.adapter import run_tool, format_error, _serialize
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.metrics_service import MetricsService
from backend.app.services.audit_log_service import AuditLogService
from backend.app.services.error_log_service import ErrorLogService


def register_observability_tools(mcp) -> None:

    @mcp.tool()
    async def ping() -> str:
        """
        Check MCP server health and database connectivity.
        Returns server status, app name, environment, and DB ping result.
        """
        try:
            db = get_db()
            await db.command("ping")
            from backend.app.core.config import settings
            return _serialize({
                "status": "ok",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "database": "connected",
                "architecture": "MCP → Services → MongoDB (no HTTP)",
            })
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    async def get_analytics() -> str:
        """
        Get the full operational analytics dashboard.
        Includes: executive summary, revenue stats, top books, associate performance,
        review metrics, low stock alerts, stale requests, and inactive projects.
        Best used to answer: 'How is the store performing?' or 'What needs attention?'
        """
        return await run_tool(AnalyticsService(get_db()).get_analytics)

    @mcp.tool()
    async def get_metrics_summary() -> str:
        """
        Get aggregated metric counters — logins, orders, new users, books added, etc.
        Returns current totals and a comparison to the previous period.
        """
        return await run_tool(MetricsService(get_db()).get_summary)

    @mcp.tool()
    async def get_metrics_trend() -> str:
        """
        Get 30-day hourly metric trend data suitable for charting.
        Use this to identify patterns in user activity, orders, or errors over time.
        """
        return await run_tool(MetricsService(get_db()).get_trend)

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
        try:
            from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00")) if from_date else None
        except (ValueError, AttributeError):
            return "ERROR [VALIDATION]: from_date must be ISO 8601 format e.g. '2026-01-01T00:00:00Z'"
        return await run_tool(
            AuditLogService(get_db()).get_logs,
            page=page, page_size=page_size,
            action=action, actor_id=actor_id,
            entity_type=entity_type, from_date=from_dt,
        )

    @mcp.tool()
    async def get_entity_audit_logs(entity_type: str, entity_id: str) -> str:
        """
        Get the full audit trail for a specific entity.
        Args:
            entity_type: Type of entity — 'book', 'order', 'project', 'user', 'review'.
            entity_id: MongoDB ObjectId string of the entity.
        """
        return await run_tool(
            AuditLogService(get_db()).get_entity_logs,
            entity_type, entity_id,
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
        try:
            from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00")) if from_date else None
        except (ValueError, AttributeError):
            return "ERROR [VALIDATION]: from_date must be ISO 8601 format e.g. '2026-01-01T00:00:00Z'"
        return await run_tool(
            ErrorLogService(get_db()).get_logs,
            page=page, page_size=page_size,
            level=level, endpoint=endpoint, from_date=from_dt,
        )