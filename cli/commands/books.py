"""Book catalog commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..http import ApiClient, ApiError

app = typer.Typer(help="Browse the book catalog.")
console = Console()


def _format_authors(authors: list[str]) -> str:
    return ", ".join(authors) if authors else "—"


@app.command("list")
def list_books(
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number."),
    page_size: int = typer.Option(20, "--page-size", "-n", min=1, max=100, help="Items per page."),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Text search."),
    category: Optional[str] = typer.Option(None, "--category", help="Filter by category."),
    author: Optional[str] = typer.Option(None, "--author", help="Filter by author."),
    min_price: Optional[float] = typer.Option(None, "--min-price", min=0, help="Minimum price."),
    max_price: Optional[float] = typer.Option(None, "--max-price", min=0, help="Maximum price."),
    in_stock_only: bool = typer.Option(False, "--in-stock-only", help="Show only in-stock books."),
) -> None:
    """List books (public endpoint)."""
    params: dict[str, object] = {"page": page, "page_size": page_size}
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
    if in_stock_only:
        params["in_stock_only"] = True

    try:
        data = ApiClient().get("books", params=params)
    except ApiError as exc:
        label = f"Error {exc.status_code}" if exc.status_code else "Connection error"
        console.print(f"[red]{label}:[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    items = data.get("items", [])
    table = Table(title="Books", show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Title")
    table.add_column("Authors")
    table.add_column("Price", justify="right")
    table.add_column("Stock", justify="right")
    table.add_column("Active", justify="center")

    for book in items:
        table.add_row(
            book.get("id", ""),
            book.get("title", ""),
            _format_authors(book.get("authors", [])),
            f"${book.get('price', 0):.2f}",
            str(book.get("stock", 0)),
            "✓" if book.get("is_active") else "✗",
        )

    console.print(table)
    console.print(
        f"Page {data.get('page', page)} of {data.get('total_pages', 1)} "
        f"({data.get('total', len(items))} total)"
    )


@app.command("get")
def get_book(
    book_id: str = typer.Argument(..., help="Book ID."),
) -> None:
    """Get a single book by ID (public endpoint)."""
    try:
        book = ApiClient().get(f"books/{book_id}")
    except ApiError as exc:
        label = f"Error {exc.status_code}" if exc.status_code else "Connection error"
        console.print(f"[red]{label}:[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    console.print(f"[bold]{book.get('title', 'Unknown')}[/bold]")
    console.print(f"[dim]ID:[/dim] {book.get('id', '')}")
    console.print(f"[dim]Authors:[/dim] {_format_authors(book.get('authors', []))}")
    console.print(f"[dim]Categories:[/dim] {', '.join(book.get('categories', [])) or '—'}")
    console.print(f"[dim]Price:[/dim] ${book.get('price', 0):.2f}")
    console.print(f"[dim]Stock:[/dim] {book.get('stock', 0)}")
    if book.get("is_low_stock"):
        console.print("[yellow]Low stock[/yellow]")
    console.print(f"[dim]Publisher:[/dim] {book.get('publisher') or '—'}")
    console.print(f"[dim]ISBN:[/dim] {book.get('isbn') or '—'}")
    console.print(f"[dim]Edition:[/dim] {book.get('edition') or '—'}")
    console.print(f"[dim]Language:[/dim] {book.get('language') or '—'}")
    if description := book.get("description"):
        console.print(f"\n{description}")
