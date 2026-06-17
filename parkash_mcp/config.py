"""
MCP server configuration.

The MCP server talks to the Parkash Book Depot backend over HTTP instead of
connecting to MongoDB directly. By default it targets the production
deployment on Railway. Override with the PARKASH_API_URL environment
variable (e.g. to point at a local backend during development).
"""

from __future__ import annotations

import os

DEFAULT_BASE_URL = "https://parkash-book-depot-production.up.railway.app/api/v1"


def get_base_url() -> str:
    """Return the API base URL, honoring the PARKASH_API_URL override."""
    return os.environ.get("PARKASH_API_URL", DEFAULT_BASE_URL).rstrip("/")


def get_admin_email() -> str | None:
    return os.environ.get("PARKASH_ADMIN_EMAIL")


def get_admin_password() -> str | None:
    return os.environ.get("PARKASH_ADMIN_PASSWORD")


def get_static_access_token() -> str | None:
    """An already-issued access token, bypassing the login flow entirely."""
    return os.environ.get("PARKASH_ACCESS_TOKEN")
