"""User management commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..http import ApiClient, ApiError

app = typer.Typer(help="View users (admin).")
console = Console()


@app.command("list")
def list_users() -> None:
    """List all users. Requires admin authentication."""
    try:
        users = ApiClient(require_auth=True).get("users")
    except ApiError as exc:
        label = f"Error {exc.status_code}" if exc.status_code else "Connection error"
        console.print(f"[red]{label}:[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    table = Table(title="Users", show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Role")
    table.add_column("Active", justify="center")

    for user in users:
        table.add_row(
            user.get("id", ""),
            user.get("name", ""),
            user.get("email", ""),
            user.get("role", ""),
            "✓" if user.get("is_active") else "✗",
        )

    console.print(table)
    console.print(f"{len(users)} user(s)")
