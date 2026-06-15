"""MCP tools for browsing the book catalog."""

from __future__ import annotations

from typing import Any
from parkash_mcp.adapter import execute_get


def register_book_tools(mcp: Any) -> None:
    """Register book catalog tools with the FastMCP instance."""
    
    @mcp.tool()
    async def list_books(
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        category: str | None = None,
        author: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        in_stock_only: bool = False,
    ) -> dict[str, Any]:
        """List books from the catalog with optional search and filter criteria.
        
        Args:
            page: Page number for pagination (default: 1).
            page_size: Number of items per page (default: 20, max: 100).
            search: Text search query to search titles, description, or authors.
            category: Filter books by a specific category.
            author: Filter books by a specific author.
            min_price: Filter books with price greater than or equal to this.
            max_price: Filter books with price less than or equal to this.
            in_stock_only: Set to true to list only books currently in stock.
            
        Returns:
            A dict containing list of books and pagination metadata.
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "in_stock_only": in_stock_only,
        }
        
        if search:
            params["search"] = search
        if category:
            params["category"] = category
        if author:
            params["author"] = author
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price

        return await execute_get("books", params=params)

    @mcp.tool()
    async def get_book(book_id: str) -> dict[str, Any]:
        """Retrieve details of a single book by its ID.
        
        Args:
            book_id: The unique ID of the book.
            
        Returns:
            A dict containing book details like authors, categories, price, stock, description.
        """
        return await execute_get(f"books/{book_id}")
