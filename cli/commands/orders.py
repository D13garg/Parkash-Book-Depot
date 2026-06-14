"""Order commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..http import ApiClient, ApiError

app = typer.Typer(help="View orders.")
console = Console()


@app.command("list")
def list_orders(
    page: int = typer.Option(1, "--page", "-p", min=1, help="Page number."),
    page_size: int = typer.Option(20, "--page-size", "-n", min=1, max=100, help="Items per page."),
    all_orders: bool = typer.Option(
        False,
        "--all",
        help="List all orders (admin). Default: your orders (/orders/mine).",
    ),
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help="Filter by status (admin --all only): pending, confirmed, processing, shipped, delivered, cancelled.",
    ),
) -> None:
    """List orders. Requires authentication."""
    params: dict[str, object] = {"page": page, "page_size": page_size}
    path = "orders" if all_orders else "orders/mine"
    if all_orders and status:
        params["status"] = status

    try:
        data = ApiClient(require_auth=True).get(path, params=params)
    except ApiError as exc:
        label = f"Error {exc.status_code}" if exc.status_code else "Connection error"
        console.print(f"[red]{label}:[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    items = data.get("items", [])
    title = "All Orders" if all_orders else "My Orders"
    table = Table(title=title, show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Customer")
    table.add_column("Status")
    table.add_column("Items", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Created")

    for order in items:
        created = order.get("created_at", "")
        if isinstance(created, str) and "T" in created:
            created = created.replace("T", " ").rstrip("Z")
        table.add_row(
            order.get("id", ""),
            order.get("customer_name", ""),
            order.get("status", ""),
            str(len(order.get("items", []))),
            f"${order.get('total_amount', 0):.2f}",
            created[:19] if created else "—",
        )

    console.print(table)
    console.print(
        f"Page {data.get('page', page)} of {data.get('total_pages', 1)} "
        f"({data.get('total', len(items))} total)"
    )


@app.command("get")
def get_order(
    order_id: str = typer.Argument(..., help="Order ID."),
) -> None:
    """Get a single order by ID. Requires authentication (owner or admin)."""
    try:
        order = ApiClient(require_auth=True).get(f"orders/{order_id}")
    except ApiError as exc:
        label = f"Error {exc.status_code}" if exc.status_code else "Connection error"
        console.print(f"[red]{label}:[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    console.print(f"[bold]Order {order.get('id', '')}[/bold]")
    console.print(f"[dim]Customer:[/dim] {order.get('customer_name', '')}")
    console.print(f"[dim]Status:[/dim] {order.get('status', '')}")
    console.print(f"[dim]Total:[/dim] ${order.get('total_amount', 0):.2f}")
    console.print(f"[dim]Address:[/dim] {order.get('delivery_address', '')}")
    console.print(f"[dim]Phone:[/dim] {order.get('phone', '')}")
    if notes := order.get("notes"):
        console.print(f"[dim]Notes:[/dim] {notes}")

    items = order.get("items", [])
    if items:
        table = Table(title="Line Items", show_lines=False)
        table.add_column("Book ID", style="dim")
        table.add_column("Title")
        table.add_column("Price", justify="right")
        table.add_column("Qty", justify="right")
        table.add_column("Subtotal", justify="right")

        for item in items:
            table.add_row(
                item.get("book_id", ""),
                item.get("title", ""),
                f"${item.get('price', 0):.2f}",
                str(item.get("quantity", 0)),
                f"${item.get('subtotal', 0):.2f}",
            )

        console.print(table)
