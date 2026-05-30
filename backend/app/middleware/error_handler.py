import traceback
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import get_database

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catches all unhandled exceptions.
    Logs them to MongoDB error_logs collection.
    Returns a clean JSON response instead of exposing stack traces.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)

            # Log 4xx/5xx responses that slipped through
            if response.status_code >= 500:
                await self._log(
                    request=request,
                    message=f"HTTP {response.status_code} on {request.method} {request.url.path}",
                    level="ERROR",
                    status_code=response.status_code,
                )
            elif response.status_code == 403:
                await self._log(
                    request=request,
                    message=f"Permission denied: {request.method} {request.url.path}",
                    level="WARNING",
                    status_code=403,
                )

            return response

        except Exception as exc:
            tb = traceback.format_exc()
            logger.error(f"Unhandled exception: {exc}\n{tb}")

            await self._log(
                request=request,
                message=str(exc),
                level="ERROR",
                stack_trace=tb,
                status_code=500,
            )

            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred."},
            )

    async def _log(
        self,
        request: Request,
        message: str,
        level: str,
        stack_trace: str = None,
        status_code: int = None,
    ):
        try:
            from app.services.error_log_service import log_error
            db = get_database()
            if db is None:
                return
            await log_error(
                db=db,
                message=message,
                level=level,
                endpoint=str(request.url.path),
                method=request.method,
                stack_trace=stack_trace,
                ip_address=request.client.host if request.client else None,
                status_code=status_code,
            )
        except Exception:
            pass