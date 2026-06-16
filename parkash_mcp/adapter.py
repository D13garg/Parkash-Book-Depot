"""
MCP Exception Adapter

Translates AppException subclasses into clean MCP error strings.
AppException.detail is a plain string — readable without any FastAPI involvement.

All MCP tools call run_tool() which centralises the try/except so tool
functions stay clean and focused on business logic only.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Coroutine

from backend.app.core.exceptions import (
    AppException,
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    BadRequestException,
    ConflictException,
    TooManyRequestsException,
    InvalidStateTransitionException,
)

logger = logging.getLogger(__name__)


def _serialize(data: Any) -> str:
    """Serialize result to formatted JSON string."""
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), indent=2, default=str)
    if isinstance(data, list):
        return json.dumps(
            [r.model_dump() if hasattr(r, "model_dump") else r for r in data],
            indent=2, default=str,
        )
    if isinstance(data, dict):
        return json.dumps(data, indent=2, default=str)
    return str(data)


def format_error(exc: Exception) -> str:
    """Translate any exception into a clean MCP error string."""
    if isinstance(exc, InvalidStateTransitionException):
        return f"ERROR [STATE_TRANSITION]: {exc.detail}"
    if isinstance(exc, NotFoundException):
        return f"ERROR [NOT_FOUND]: {exc.detail}"
    if isinstance(exc, ForbiddenException):
        return f"ERROR [FORBIDDEN]: {exc.detail}"
    if isinstance(exc, UnauthorizedException):
        return f"ERROR [UNAUTHORIZED]: {exc.detail}"
    if isinstance(exc, BadRequestException):
        return f"ERROR [BAD_REQUEST]: {exc.detail}"
    if isinstance(exc, ConflictException):
        return f"ERROR [CONFLICT]: {exc.detail}"
    if isinstance(exc, TooManyRequestsException):
        return f"ERROR [RATE_LIMITED]: {exc.detail}"
    if isinstance(exc, AppException):
        return f"ERROR [{exc.status_code}]: {exc.detail}"
    if isinstance(exc, RuntimeError):
        # email_service raises RuntimeError — catch separately
        logger.error(f"RuntimeError in MCP tool: {exc}")
        return f"ERROR [RUNTIME]: {exc}"
    logger.exception(f"Unexpected error in MCP tool: {exc}")
    return f"ERROR [INTERNAL]: {type(exc).__name__}: {exc}"


async def run_tool(coro_fn: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> str:
    """
    Execute a service coroutine and return a formatted result string.

    Usage:
        return await run_tool(BookService(db).get_books)
        return await run_tool(BookService(db).get_book, book_id)
        return await run_tool(BookService(db).create_book, data, MCP_USER)
    """
    try:
        result = await coro_fn(*args, **kwargs)
        return _serialize(result)
    except (AppException, RuntimeError) as e:
        return format_error(e)
    except Exception as e:
        return format_error(e)