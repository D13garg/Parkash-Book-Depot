"""Projects tools — 11 tools."""
from __future__ import annotations
from typing import Optional
from parkash_mcp.context import get_db, MCP_USER
from parkash_mcp.adapter import run_tool, format_error
from backend.app.services.project_service import ProjectService
from backend.app.services.project_request_service import ProjectRequestService
from backend.app.schemas.project import (
    AssignProjectRequest,
    UpdateProjectStatusRequest,
    CreateProjectUpdateRequest,
)
from backend.app.schemas.project_request import UpdateRequestStatusRequest


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
        return await run_tool(
            ProjectRequestService(get_db()).get_requests,
            MCP_USER, page=page, page_size=page_size,
            status=status, request_type=request_type,
        )

    @mcp.tool()
    async def get_project_request(request_id: str) -> str:
        """
        Get full details of a single project request.
        Args:
            request_id: MongoDB ObjectId string of the request.
        """
        return await run_tool(
            ProjectRequestService(get_db()).get_request,
            request_id, MCP_USER,
        )

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
        try:
            data = UpdateRequestStatusRequest(status=status, admin_notes=admin_notes)
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(
            ProjectRequestService(get_db()).update_status,
            request_id, data, MCP_USER,
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
            ProjectService(get_db()).convert_request_to_project,
            request_id, MCP_USER,
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
        return await run_tool(
            ProjectService(get_db()).get_projects,
            MCP_USER, page=page, page_size=page_size, status=status,
        )

    @mcp.tool()
    async def get_project(project_id: str) -> str:
        """
        Get full details of a single project.
        Args:
            project_id: MongoDB ObjectId string of the project.
        """
        return await run_tool(
            ProjectService(get_db()).get_project,
            project_id, MCP_USER,
        )

    @mcp.tool()
    async def get_project_updates(project_id: str) -> str:
        """
        Get the full progress update timeline for a project.
        Args:
            project_id: MongoDB ObjectId string of the project.
        """
        return await run_tool(
            ProjectService(get_db()).get_updates,
            project_id, MCP_USER,
        )

    @mcp.tool()
    async def assign_project_associate(project_id: str, associate_id: str) -> str:
        """
        Assign an associate to a project.
        Use list_associates first to get valid associate IDs.
        Args:
            project_id: MongoDB ObjectId string of the project.
            associate_id: MongoDB ObjectId string of the associate user.
        """
        try:
            data = AssignProjectRequest(associate_id=associate_id)
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(
            ProjectService(get_db()).assign_associate,
            project_id, data, MCP_USER,
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
        try:
            data = UpdateProjectStatusRequest(status=status)
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(
            ProjectService(get_db()).update_status,
            project_id, data, MCP_USER,
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
        try:
            data = CreateProjectUpdateRequest(
                title=title,
                content=content,
                progress_percentage=progress_percentage,
            )
        except Exception as e:
            return f"ERROR [VALIDATION]: {e}"
        return await run_tool(
            ProjectService(get_db()).add_update,
            project_id, data, MCP_USER,
        )