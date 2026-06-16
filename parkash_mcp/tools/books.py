"""Books tools — 6 tools."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_db, MCP_USER
from parkash_mcp.adapter import run_tool, format_error
from backend.app.services.book_service import BookService
from backend.app.schemas.book import CreateBookRequest, UpdateBookRequest


def register_book_tools(mcp) -> None:

    @mcp.tool()
    async def list_books(
        search: Optional[str] = None,
        category: Optional[str] = None,
        author: Optional[str] = None,
        in_stock_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> str:
        """
        List and search books in the catalogue with optional filters.
        Args:
            search: Full-text search across title, author, description.
            category: Filter by category tag e.g. 'textbook', 'cbse', 'class-9'.
            author: Filter by author name.
            in_stock_only: Only return books with stock > 0.
            min_price: Minimum price in INR.
            max_price: Maximum price in INR.
            page: Page number (default 1).
            page_size: Results per page (default 20).
        """
        return await run_tool(
            BookService(get_db()).get_books,
            page=page, page_size=page_size, category=category,
            author=author, min_price=min_price, max_price=max_price,
            in_stock_only=in_stock_only, search=search,
        )

    @mcp.tool()
    async def get_book(book_id: str) -> str:
        """
        Get full details of a single book.
        Args:
            book_id: MongoDB ObjectId string of the book.
        """
        return await run_tool(BookService(get_db()).get_book, book_id)

    @mcp.tool()
    async def get_low_stock_books() -> str:
        """
        Return all books at or below their low_stock_threshold.
        Use this to identify restocking needs.
        """
        return await run_tool(BookService(get_db()).get_low_stock_books)

    @mcp.tool()
    async def create_book(
        title: str,
        authors: list[str],
        price: float,
        stock: int,
        categories: list[str],
        publisher: Optional[str] = None,
        isbn: Optional[str] = None,
        description: Optional[str] = None,
        edition: Optional[str] = None,
        language: str = "English",
        low_stock_threshold: int = 5,
    ) -> str:
        """
        Add a new book to the catalogue.
        Args:
            title: Book title.
            authors: List of author names.
            price: Price in INR (must be > 0).
            stock: Initial stock quantity.
            categories: List of category tags e.g. ['textbook', 'cbse', 'class-9'].
            publisher: Publisher name.
            isbn: ISBN number.
            description: Book description.
            edition: Edition e.g. '2026'.
            language: Language (default 'English').
            low_stock_threshold: Alert threshold (default 5).
        """
        try:
            data = CreateBookRequest(
                title=title, authors=authors, price=price, stock=stock,
                categories=categories, publisher=publisher, isbn=isbn,
                description=description, edition=edition, language=language,
                low_stock_threshold=low_stock_threshold,
            )
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(BookService(get_db()).create_book, data, MCP_USER)

    @mcp.tool()
    async def update_book(
        book_id: str,
        title: Optional[str] = None,
        price: Optional[float] = None,
        publisher: Optional[str] = None,
        description: Optional[str] = None,
        edition: Optional[str] = None,
        language: Optional[str] = None,
        isbn: Optional[str] = None,
        low_stock_threshold: Optional[int] = None,
    ) -> str:
        """
        Update fields on an existing book. Only provided fields are changed.
        Args:
            book_id: MongoDB ObjectId string of the book.
            title: New title.
            price: New price in INR.
            publisher: Publisher name.
            description: Book description.
            edition: Edition string.
            language: Language.
            isbn: ISBN number.
            low_stock_threshold: New low stock alert threshold.
        """
        try:
            data = UpdateBookRequest(
                title=title, price=price, publisher=publisher,
                description=description, edition=edition,
                language=language, isbn=isbn,
                low_stock_threshold=low_stock_threshold,
            )
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(BookService(get_db()).update_book, book_id, data, MCP_USER)

    @mcp.tool()
    async def update_book_stock(book_id: str, new_stock: int) -> str:
        """
        Set the stock level for a book.
        Args:
            book_id: MongoDB ObjectId string of the book.
            new_stock: New stock quantity (must be >= 0).
        """
        return await run_tool(BookService(get_db()).update_stock, book_id, new_stock, MCP_USER)