"""
MCP HTTP Error Adapter

Translates ApiError (raised by parkash_mcp.http.ApiClient on any non-2xx
response from the backend) into clean MCP error strings. All MCP tools
call run_tool() so the try/except stays centralised and tool functions
stay focused on building the request.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Coroutine

from parkash_mcp.http import ApiError

logger = logging.getLogger(__name__)

_STATUS_LABELS = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION",
    429: "RATE_LIMITED",
}


def _serialize(data: Any) -> str:
    """Serialize a parsed JSON response (dict/list/scalar) to formatted JSON."""
    if data is None:
        return json.dumps({"message": "OK"})
    return json.dumps(data, indent=2, default=str)


def format_error(exc: Exception) -> str:
    """Translate any exception into a clean MCP error string."""
    if isinstance(exc, ApiError):
        if exc.status_code == 0:
            return f"ERROR [CONNECTION]: {exc.detail}"
        label = _STATUS_LABELS.get(exc.status_code, str(exc.status_code))
        return f"ERROR [{label}]: {exc.detail}"
    logger.exception(f"Unexpected error in MCP tool: {exc}")
    return f"ERROR [INTERNAL]: {type(exc).__name__}: {exc}"


async def run_tool(coro_fn: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> str:
    """
    Execute an HTTP call coroutine and return a formatted result string.

    Usage:
        return await run_tool(client.get, "/books")
        return await run_tool(client.post, "/books", json=payload)
    """
    try:
        result = await coro_fn(*args, **kwargs)
        return _serialize(result)
    except ApiError as e:
        return format_error(e)
    except Exception as e:
        return format_error(e)
