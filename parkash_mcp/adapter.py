"""Adapter layer to call the CLI ApiClient in worker threads and translate errors."""

from __future__ import annotations

import asyncio
from typing import Any

from cli.http import ApiError
from .context import context


class MCPError(Exception):
    """Base exception for MCP adapter errors."""
    pass


class AuthenticationError(MCPError):
    """Raised when authentication is required or fails."""
    pass


class NotFoundError(MCPError):
    """Raised when a resource is not found."""
    pass


class ConnectionError(MCPError):
    """Raised when the backend API is unreachable."""
    pass


def check_auth() -> None:
    """Verify that an access token exists in the current context.
    
    Raises:
        AuthenticationError: If the token is missing.
    """
    if not context.get_token():
        raise AuthenticationError(
            "Authentication required. Please run 'parkash auth login' in the CLI "
            "or set the 'PARKASH_ACCESS_TOKEN' environment variable to authenticate."
        )


def translate_error(exc: ApiError) -> MCPError:
    """Map cli.http.ApiError to a semantic MCP-friendly error."""
    if exc.status_code == 0:
        return ConnectionError(
            f"Could not reach the backend API at {context.client.config.base_url}. "
            f"Please verify the backend server is running and reachable. Detail: {exc.detail}"
        )
    elif exc.status_code == 401:
        return AuthenticationError(
            f"Authentication failed (401 Unauthorized). Please log in again using the CLI "
            f"or verify your access token. Detail: {exc.detail}"
        )
    elif exc.status_code == 403:
        return AuthenticationError(
            f"Permission denied (403 Forbidden). You are not authorized to perform "
            f"this action. Detail: {exc.detail}"
        )
    elif exc.status_code == 404:
        return NotFoundError(f"Resource not found (404). Detail: {exc.detail}")
    else:
        return MCPError(f"Backend API returned error {exc.status_code}: {exc.detail}")


async def execute_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Execute a GET request using the ApiClient in a separate thread.
    
    Args:
        path: API path relative to the base URL.
        params: Optional query parameters.
        
    Returns:
        The JSON response from the API.
        
    Raises:
        MCPError: If the request fails.
    """
    try:
        # Offload synchronous HTTP request to a worker thread to keep the event loop responsive
        return await asyncio.to_thread(context.client.get, path, params=params)
    except ApiError as exc:
        raise translate_error(exc) from exc
    except Exception as exc:
        raise MCPError(f"An unexpected error occurred: {exc}") from exc


async def execute_post(path: str, json_data: dict[str, Any]) -> Any:
    """Execute a POST request using the ApiClient in a separate thread.
    
    Args:
        path: API path relative to the base URL.
        json_data: JSON payload dictionary.
        
    Returns:
        The JSON response from the API.
        
    Raises:
        MCPError: If the request fails.
    """
    try:
        # Offload synchronous HTTP request to a worker thread to keep the event loop responsive
        return await asyncio.to_thread(context.client.post, path, json=json_data)
    except ApiError as exc:
        raise translate_error(exc) from exc
    except Exception as exc:
        raise MCPError(f"An unexpected error occurred: {exc}") from exc
