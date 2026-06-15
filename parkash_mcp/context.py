"""Context management for the MCP server, wrapping the CLI ApiClient."""

from __future__ import annotations

from cli.config import load_config
from cli.http import ApiClient


class MCPContext:
    """Manages the lifecycle and state of the CLI ApiClient for the MCP server."""

    def __init__(self) -> None:
        # Load the configuration from the CLI storage or environment variables.
        self.config = load_config()
        
        # Instantiate the ApiClient with require_auth=False to prevent SystemExit(1)
        # when an access token is missing. Instead, we'll perform validation
        # in the adapter/tools layer and raise clean exceptions.
        self._client = ApiClient(require_auth=False, config=self.config)

    @property
    def client(self) -> ApiClient:
        """Get the shared ApiClient instance."""
        return self._client

    def get_token(self) -> str | None:
        """Get the current access token."""
        return self.config.access_token


# Global singleton context
context = MCPContext()
