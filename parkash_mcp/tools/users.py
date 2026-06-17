"""Users tools — 4 tools. Calls the backend over HTTP instead of MongoDB."""
from __future__ import annotations
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool, _serialize, format_error
from parkash_mcp.http import ApiError


def register_user_tools(mcp) -> None:

    @mcp.tool()
    async def list_users(
        role: str = "all",
        active_only: bool = False,
    ) -> str:
        """
        List all users (customers, associates, admins).
        Args:
            role: Filter by role — 'all', 'customer', 'associate', 'admin'.
            active_only: If true, only return active accounts.
        """
        try:
            users = await get_client().get("/users")
            if role != "all":
                users = [u for u in users if u.get("role") == role]
            if active_only:
                users = [u for u in users if u.get("is_active")]
            return _serialize(users)
        except ApiError as e:
            return format_error(e)

    @mcp.tool()
    async def list_associates() -> str:
        """
        List all associate accounts (active only).
        Use this before assigning a project to get valid associate IDs and names.
        """
        return await run_tool(get_client().get, "/users/associates")

    @mcp.tool()
    async def deactivate_user(user_id: str) -> str:
        """
        Deactivate a user account. The user will be unable to log in.
        Cannot deactivate admin accounts. Reversible via reactivate_user.
        Args:
            user_id: MongoDB ObjectId string of the user.
        """
        return await run_tool(get_client().patch, f"/users/{user_id}/deactivate", json={})

    @mcp.tool()
    async def reactivate_user(user_id: str) -> str:
        """
        Reactivate a previously deactivated user account.
        Args:
            user_id: MongoDB ObjectId string of the user.
        """
        return await run_tool(get_client().patch, f"/users/{user_id}/reactivate", json={})
