"""
HTTP client for the Parkash Book Depot backend.

The MCP server used to talk to MongoDB directly via the same Motor client
as the FastAPI app (no HTTP round-trips). It now runs against the deployed
backend over HTTPS instead, so every tool call becomes a request to
PARKASH_API_URL (defaults to the Railway production deployment).

Auth: most admin endpoints require a JWT bearer token. On first request,
the client logs in with PARKASH_ADMIN_EMAIL / PARKASH_ADMIN_PASSWORD (or
uses PARKASH_ACCESS_TOKEN directly if provided) and caches the access
token in memory for the life of the process. A 401 triggers exactly one
re-login attempt before giving up, in case the token expired mid-session.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from parkash_mcp.config import (
    get_admin_email,
    get_admin_password,
    get_base_url,
    get_static_access_token,
)

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Raised for any non-2xx response from the backend."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ApiClient:
    """
    Thin async HTTP client with lazy login and in-memory token caching.

    A single instance is shared for the lifetime of the MCP server process
    (see context.py), so the login round-trip only happens once.
    """

    def __init__(self) -> None:
        self._access_token: str | None = get_static_access_token()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=get_base_url(), timeout=30.0)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _login(self) -> None:
        email = get_admin_email()
        password = get_admin_password()
        if not email or not password:
            raise ApiError(
                401,
                "Not authenticated. Set PARKASH_ACCESS_TOKEN, or both "
                "PARKASH_ADMIN_EMAIL and PARKASH_ADMIN_PASSWORD, as "
                "environment variables for the MCP server.",
            )
        client = await self._get_client()
        response = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        self._raise_for_status(response)
        data = response.json()
        self._access_token = data["access_token"]

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        detail = response.text
        try:
            body = response.json()
            raw = body.get("detail", detail)
            if isinstance(raw, list):
                detail = "; ".join(str(item) for item in raw)
            else:
                detail = str(raw)
        except Exception:
            pass
        raise ApiError(response.status_code, detail)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        _retried: bool = False,
    ) -> Any:
        if self._access_token is None and (get_admin_email() and get_admin_password()):
            await self._login()

        client = await self._get_client()
        try:
            response = await client.request(
                method, path, headers=self._headers(), params=params, json=json
            )
        except httpx.RequestError as exc:
            raise ApiError(
                0, f"Could not reach API at {get_base_url()}: {exc}"
            ) from exc

        if response.status_code == 401 and not _retried and get_admin_email() and get_admin_password():
            # Token may have expired — log in once more and retry.
            await self._login()
            return await self._request(
                method, path, params=params, json=json, _retried=True
            )

        self._raise_for_status(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", path, json=json)

    async def put(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return await self._request("PUT", path, json=json)

    async def patch(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str) -> Any:
        return await self._request("DELETE", path)
