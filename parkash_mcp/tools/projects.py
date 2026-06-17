"""Projects tools — 11 tools. Calls the backend over HTTP instead of MongoDB."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool


def register_project_tools(mcp) -> None:

    # ── Project Requests ──────────────────────────────────────────────────────

    @mcp.tool()
    async def list_project_requests(
        status: Optional[str] = None,
        request_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> str:
        """
        List all customer project requests.
        Args:
            status: Filter by status — submitted, under_review, accepted, rejected, converted_to_project.
            request_type: Filter by type — 'project' or 'other'.
            page: Page number (default 1).
            page_size: Results per page (default 20).
        """
        params = {
            "page": page, "page_size": page_size,
            "status": status, "request_type": request_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await run_tool(get_client().get, "/project-requests", params=params)

    @mcp.tool()
    async def get_project_request(request_id: str) -> str:
        """
        Get full details of a single project request.
        Args:
            request_id: MongoDB ObjectId string of the request.
        """
        return await run_tool(get_client().get, f"/project-requests/{request_id}")

    @mcp.tool()
    async def update_request_status(request_id: str, status: str, admin_notes: Optional[str] = None) -> str:
        """
        Update the status of a project request.
        Valid transitions: submitted→under_review, under_review→accepted/rejected.
        Args:
            request_id: MongoDB ObjectId string of the request.
            status: New status — under_review, accepted, rejected.
            admin_notes: Optional notes to attach to the status change.
        """
        payload = {"status": status, "admin_notes": admin_notes}
        payload = {k: v for k, v in payload.items() if v is not None}
        return await run_tool(
            get_client().patch, f"/project-requests/{request_id}/status", json=payload
        )

    @mcp.tool()
    async def convert_request_to_project(request_id: str) -> str:
        """
        Convert an accepted project request into a live project.
        The request must be in 'accepted' status before conversion.
        Args:
            request_id: MongoDB ObjectId string of the accepted request.
        """
        return await run_tool(
            get_client().post, f"/projects/from-request/{request_id}", json={}
        )

    # ── Projects ──────────────────────────────────────────────────────────────

    @mcp.tool()
    async def list_projects(
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> str:
        """
        List all projects.
        Args:
            status: Filter by status — pending, assigned, in_progress, waiting_supplier, completed, cancelled.
            page: Page number (default 1).
            page_size: Results per page (default 20).
        """
        params = {"page": page, "page_size": page_size, "status": status}
        params = {k: v for k, v in params.items() if v is not None}
        return await run_tool(get_client().get, "/projects", params=params)

    @mcp.tool()
    async def get_project(project_id: str) -> str:
        """
        Get full details of a single project.
        Args:
            project_id: MongoDB ObjectId string of the project.
        """
        return await run_tool(get_client().get, f"/projects/{project_id}")

    @mcp.tool()
    async def get_project_updates(project_id: str) -> str:
        """
        Get the full progress update timeline for a project.
        Args:
            project_id: MongoDB ObjectId string of the project.
        """
        return await run_tool(get_client().get, f"/projects/{project_id}/updates")

    @mcp.tool()
    async def assign_project_associate(project_id: str, associate_id: str) -> str:
        """
        Assign an associate to a project.
        Use list_associates first to get valid associate IDs.
        Args:
            project_id: MongoDB ObjectId string of the project.
            associate_id: MongoDB ObjectId string of the associate user.
        """
        return await run_tool(
            get_client().patch,
            f"/projects/{project_id}/assign",
            json={"associate_id": associate_id},
        )

    @mcp.tool()
    async def update_project_status(project_id: str, status: str) -> str:
        """
        Update the status of a project. State machine enforced server-side.
        Valid transitions: pending→assigned, assigned→in_progress,
        in_progress→waiting_supplier/completed/cancelled,
        waiting_supplier→in_progress/completed/cancelled.
        Args:
            project_id: MongoDB ObjectId string of the project.
            status: New status value.
        """
        return await run_tool(
            get_client().patch, f"/projects/{project_id}/status", json={"status": status}
        )

    @mcp.tool()
    async def add_project_update(
        project_id: str,
        title: str,
        content: str,
        progress_percentage: Optional[int] = None,
    ) -> str:
        """
        Add a progress update to a project timeline.
        Args:
            project_id: MongoDB ObjectId string of the project.
            title: Short update title e.g. 'Materials sourced'.
            content: Detailed update description.
            progress_percentage: Optional progress indicator 0-100.
        """
        payload = {"title": title, "content": content, "progress_percentage": progress_percentage}
        payload = {k: v for k, v in payload.items() if v is not None}
        return await run_tool(
            get_client().post, f"/projects/{project_id}/updates", json=payload
        )
