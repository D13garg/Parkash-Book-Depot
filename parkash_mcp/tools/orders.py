"""MCP tools for managing and viewing orders."""

from __future__ import annotations

from typing import Any
from parkash_mcp.adapter import check_auth, execute_get


def register_order_tools(mcp: Any) -> None:
    """Register order tools with the FastMCP instance."""
    
    @mcp.tool()
    async def list_orders(
        page: int = 1,
        page_size: int = 20,
        all_orders: bool = False,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List orders. Requires the client to be logged in.
        
        Args:
            page: Page number for pagination (default: 1).
            page_size: Number of items per page (default: 20, max: 100).
            all_orders: Set to true to list all orders (requires Admin role). 
                         Defaults to false, which lists only your orders.
            status: Filter orders by status (Admin only: pending, confirmed, processing, shipped, delivered, cancelled).
            
        Returns:
            A dict containing a list of orders and pagination metadata.
        """
        check_auth()
        
        path = "orders" if all_orders else "orders/mine"
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if all_orders and status:
            params["status"] = status
            
        return await execute_get(path, params=params)

    @mcp.tool()
    async def get_order(order_id: str) -> dict[str, Any]:
        """Retrieve details of a single order by its ID. Requires client to be logged in.
        
        Args:
            order_id: The unique ID of the order.
            
        Returns:
            A dict containing order details (customer, items, status, address, phone).
        """
        check_auth()
        return await execute_get(f"orders/{order_id}")
