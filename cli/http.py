"""Thin HTTP client for the Parkash Book Depot API."""

from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from .config import Config, load_config

console = Console()


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ApiClient:
    def __init__(self, *, require_auth: bool = False, config: Config | None = None) -> None:
        self.config = config or load_config()
        self.require_auth = require_auth

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"
        elif self.require_auth:
            console.print(
                "[red]Not authenticated.[/red] Run [bold]parkash auth login[/bold] "
                "or set [bold]PARKASH_ACCESS_TOKEN[/bold]."
            )
            raise SystemExit(1)
        return headers

    def _url(self, path: str) -> str:
        return f"{self.config.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self._url(path), headers=self._headers(), params=params)
                self._raise_for_status(response)
                return response.json()
        except httpx.RequestError as exc:
            raise ApiError(0, f"Could not reach API at {self.config.base_url}: {exc}") from exc

    def post(self, path: str, *, json: dict[str, Any]) -> Any:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self._url(path), headers=self._headers(), json=json)
                self._raise_for_status(response)
                return response.json()
        except httpx.RequestError as exc:
            raise ApiError(0, f"Could not reach API at {self.config.base_url}: {exc}") from exc

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
