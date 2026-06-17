from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.security import CSRF_TOKEN_COOKIE


# Routes that establish a session — no CSRF cookie exists yet
CSRF_EXEMPT_PATHS = {
    f"{settings.API_V1_PREFIX}/auth/login",
    f"{settings.API_V1_PREFIX}/auth/register/initiate",
    f"{settings.API_V1_PREFIX}/auth/register/verify",
    f"{settings.API_V1_PREFIX}/auth/google",
    f"{settings.API_V1_PREFIX}/auth/forgot-password/initiate",
    f"{settings.API_V1_PREFIX}/auth/forgot-password/verify",
}


class CsrfMiddleware(BaseHTTPMiddleware):
    """
    Double-submit cookie CSRF protection for cookie-authenticated browser clients.
    Skips validation for safe methods, Bearer-token clients (CLI/MCP), and
    session-establishing auth endpoints.
    """
    async def dispatch(self, request: Request, call_next):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            return await call_next(request)

        if request.url.path in CSRF_EXEMPT_PATHS:
            return await call_next(request)

        csrf_cookie = request.cookies.get(CSRF_TOKEN_COOKIE)
        # No CSRF cookie → non-browser client (CLI/MCP) using Bearer or body tokens
        if not csrf_cookie:
            return await call_next(request)

        csrf_header = request.headers.get("x-csrf-token")

        if not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF validation failed."},
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds standard security headers to every response.
    These tell browsers how to handle the content securely.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent browsers from MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Force HTTPS in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Disable referrer for privacy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        # Content Security Policy — restricts what resources the browser can load
        # API responses are JSON, not HTML, so a strict CSP is safe here
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "frame-ancestors 'none';"   # belt-and-suspenders with X-Frame-Options
        )

        # Remove server fingerprint
        if "server" in response.headers:
            del response.headers["server"]
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests larger than MAX_REQUEST_SIZE_MB.
    Prevents memory exhaustion from large payloads.
    """
    async def dispatch(self, request: Request, call_next):
        max_bytes = settings.MAX_REQUEST_SIZE_MB * 1024 * 1024

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request too large. Maximum size is {settings.MAX_REQUEST_SIZE_MB}MB."}
            )

        return await call_next(request)
