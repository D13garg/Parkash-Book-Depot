"""Orders tools — 3 tools. Calls the backend over HTTP instead of MongoDB."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool


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
        params = {"page": page, "page_size": page_size, "status": status}
        params = {k: v for k, v in params.items() if v is not None}
        return await run_tool(get_client().get, "/orders", params=params)

    @mcp.tool()
    async def get_order(order_id: str) -> str:
        """
        Get full details of a single order including line items.
        Args:
            order_id: MongoDB ObjectId string of the order.
        """
        return await run_tool(get_client().get, f"/orders/{order_id}")

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
        return await run_tool(
            get_client().patch, f"/orders/{order_id}/status", json={"status": status}
        )
