"""Model Context Protocol (MCP) server entrypoint for Parkash Book Depot."""

from __future__ import annotations

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from parkash_mcp.tools.health import register_health_tools
from parkash_mcp.tools.books import register_book_tools
from parkash_mcp.tools.orders import register_order_tools

# Initialize the FastMCP server
mcp = FastMCP("Parkash Book Depot")

# Register tools from our modules
register_health_tools(mcp)
register_book_tools(mcp)
register_order_tools(mcp)

if __name__ == "__main__":
    # Start the MCP server using standard IO transport by default
    mcp.run()
