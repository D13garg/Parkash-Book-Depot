"""Orders tools — 3 tools."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_db, MCP_USER
from parkash_mcp.adapter import run_tool, format_error
from backend.app.services.order_service import OrderService
from backend.app.schemas.order import UpdateOrderStatusRequest


def register_order_tools(mcp) -> None:

    @mcp.tool()
    async def list_all_orders(
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> str:
        """
        List all customer orders (admin view).
        Args:
            status: Filter by status: pending, confirmed, processing, shipped, delivered, cancelled.
            page: Page number (default 1).
            page_size: Results per page (default 20).
        """
        return await run_tool(
            OrderService(get_db()).get_all_orders,
            status, page, page_size,
        )

    @mcp.tool()
    async def get_order(order_id: str) -> str:
        """
        Get full details of a single order including line items.
        Args:
            order_id: MongoDB ObjectId string of the order.
        """
        return await run_tool(OrderService(get_db()).get_order, order_id, MCP_USER)

    @mcp.tool()
    async def update_order_status(order_id: str, status: str) -> str:
        """
        Update the status of an order. State machine enforced server-side.
        Valid transitions: pending→confirmed, confirmed→processing,
        processing→shipped, shipped→delivered. pending/confirmed→cancelled.
        Args:
            order_id: MongoDB ObjectId string of the order.
            status: New status value.
        """
        try:
            data = UpdateOrderStatusRequest(status=status)
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(OrderService(get_db()).update_status, order_id, data, MCP_USER)