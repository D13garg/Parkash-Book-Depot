"""Users tools — 4 tools."""
from __future__ import annotations
from datetime import datetime, timezone
from bson import ObjectId
from parkash_mcp.context import get_db, MCP_USER
from parkash_mcp.adapter import run_tool, format_error, _serialize
from backend.app.core.exceptions import NotFoundException, BadRequestException


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
            db = get_db()
            query = {}
            if role != "all":
                query["role"] = role
            if active_only:
                query["is_active"] = True
            cursor = db["users"].find(query, {"hashed_password": 0})
            docs = await cursor.to_list(length=None)
            for d in docs:
                d["id"] = str(d.pop("_id"))
            return _serialize(docs)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    async def list_associates() -> str:
        """
        List all associate accounts (active only).
        Use this before assigning a project to get valid associate IDs and names.
        """
        try:
            db = get_db()
            cursor = db["users"].find(
                {"role": "associate", "is_active": True},
                {"hashed_password": 0},
            )
            docs = await cursor.to_list(length=None)
            for d in docs:
                d["id"] = str(d.pop("_id"))
            return _serialize(docs)
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    async def deactivate_user(user_id: str) -> str:
        """
        Deactivate a user account. The user will be unable to log in.
        Cannot deactivate admin accounts. Reversible via reactivate_user.
        Args:
            user_id: MongoDB ObjectId string of the user.
        """
        try:
            db = get_db()
            if user_id == MCP_USER.id:
                return "ERROR [BAD_REQUEST]: Cannot deactivate the MCP server identity."
            doc = await db["users"].find_one({"_id": ObjectId(user_id)})
            if not doc:
                raise NotFoundException("User")
            if doc.get("role") == "admin":
                raise BadRequestException("Cannot deactivate admin accounts.")
            await db["users"].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}},
            )
            from backend.app.services.audit_log_service import audit
            await audit(
                db=db, actor_id=MCP_USER.id, actor_name=MCP_USER.name,
                actor_role=MCP_USER.role, action="user_deactivated",
                description=f"MCP deactivated user: {doc['name']} ({doc['email']})",
                entity_type="user", entity_id=user_id,
            )
            return _serialize({"message": f"User '{doc['name']}' deactivated successfully."})
        except Exception as e:
            return format_error(e)

    @mcp.tool()
    async def reactivate_user(user_id: str) -> str:
        """
        Reactivate a previously deactivated user account.
        Args:
            user_id: MongoDB ObjectId string of the user.
        """
        try:
            db = get_db()
            doc = await db["users"].find_one({"_id": ObjectId(user_id)})
            if not doc:
                raise NotFoundException("User")
            await db["users"].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": True, "updated_at": datetime.now(timezone.utc)}},
            )
            from backend.app.services.audit_log_service import audit
            await audit(
                db=db, actor_id=MCP_USER.id, actor_name=MCP_USER.name,
                actor_role=MCP_USER.role, action="user_reactivated",
                description=f"MCP reactivated user: {doc['name']} ({doc['email']})",
                entity_type="user", entity_id=user_id,
            )
            return _serialize({"message": f"User '{doc['name']}' reactivated successfully."})
        except Exception as e:
            return format_error(e)