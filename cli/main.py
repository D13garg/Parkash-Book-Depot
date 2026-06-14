"""Parkash Book Depot developer CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from .commands import books, orders, users
from .config import CONFIG_FILE, load_config, save_config
from .http import ApiClient, ApiError

app = typer.Typer(
    name="parkash",
    help="Developer CLI for the Parkash Book Depot API.",
    no_args_is_help=True,
)
auth_app = typer.Typer(help="Authenticate and manage stored tokens.")
app.add_typer(auth_app, name="auth")
app.add_typer(books.app, name="books")
app.add_typer(orders.app, name="orders")
app.add_typer(users.app, name="users")

console = Console()


@auth_app.command("login")
def auth_login(
    email: str = typer.Option(..., "--email", "-e", prompt=True, help="Account email."),
    password: str = typer.Option(
        ...,
        "--password",
        prompt=True,
        hide_input=True,
        help="Account password.",
    ),
) -> None:
    """Log in and store access/refresh tokens locally."""
    config = load_config()
    client = ApiClient(config=config)

    try:
        data = client.post("auth/login", json={"email": email, "password": password})
    except ApiError as exc:
        console.print(f"[red]Login failed ({exc.status_code}):[/red] {exc.detail}")
        raise typer.Exit(1) from exc

    config.access_token = data["access_token"]
    config.refresh_token = data.get("refresh_token")
    save_config(config)

    user = data.get("user", {})
    console.print(f"[green]Logged in as[/green] {user.get('name', email)} ({user.get('role', 'unknown')})")
    console.print(f"[dim]Token saved to[/dim] {CONFIG_FILE}")


@auth_app.command("logout")
def auth_logout() -> None:
    """Clear stored auth tokens."""
    config = load_config()
    config.access_token = None
    config.refresh_token = None
    save_config(config)
    console.print("[green]Logged out.[/green] Tokens cleared.")


@app.command("config")
def show_config() -> None:
    """Show current CLI configuration."""
    config = load_config()
    console.print(f"[dim]API base URL:[/dim] {config.base_url}")
    console.print(f"[dim]Authenticated:[/dim] {'yes' if config.access_token else 'no'}")
    if config.access_token:
        console.print(f"[dim]Access token:[/dim] {config.access_token[:12]}…")


@app.callback()
def main(
    api_url: Optional[str] = typer.Option(
        None,
        "--api-url",
        envvar="PARKASH_API_URL",
        help="Override API base URL (default: http://localhost:8000/api/v1).",
    ),
) -> None:
    """Global options applied before subcommands."""
    if api_url:
        config = load_config()
        config.base_url = api_url.rstrip("/")
        save_config(config)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
