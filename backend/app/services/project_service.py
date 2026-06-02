import math
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.repositories.project_repository import ProjectRepository
from app.repositories.project_update_repository import ProjectUpdateRepository
from app.repositories.project_request_repository import ProjectRequestRepository
from app.schemas.project import (
    AssignProjectRequest,
    UpdateProjectStatusRequest,
    CreateProjectUpdateRequest,
    ProjectResponse,
    ProjectUpdateResponse,
)
from app.schemas.book import PaginatedResponse
from app.models.project import ProjectModel
from app.models.project_update import ProjectUpdateModel
from app.models.user import UserModel
from app.core.enums import (
    ProjectStatus,
    ProjectRequestStatus,
    is_valid_project_transition,
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    InvalidStateTransitionException,
)
from app.permissions.project_permissions import assert_can_view_project, assert_can_update_project
from app.permissions.role_permissions import is_admin, is_associate
from app.services.notification_service import notify
from app.services.audit_log_service import audit
from app.services.metrics_service import increment as inc_metric


def _to_project_response(project: ProjectModel) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        request_id=project.request_id,
        created_by=project.created_by,
        assigned_to=project.assigned_to,
        title=project.title,
        description=project.description,
        priority=project.priority,
        deadline=project.deadline,
        status=project.status,
        notes=project.notes,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _to_update_response(update: ProjectUpdateModel) -> ProjectUpdateResponse:
    return ProjectUpdateResponse(
        id=update.id,
        project_id=update.project_id,
        updated_by=update.updated_by,
        message=update.message,
        status_changed_to=update.status_changed_to,
        attachments=update.attachments,
        created_at=update.created_at,
    )


class ProjectService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.project_repo = ProjectRepository(db)
        self.update_repo = ProjectUpdateRepository(db)
        self.request_repo = ProjectRequestRepository(db)

    async def convert_request_to_project(
        self,
        request_id: str,
        current_user: UserModel,
    ) -> ProjectResponse:
        request = await self.request_repo.find_by_id(request_id)
        if not request:
            raise NotFoundException("Project request")

        if request.status != ProjectRequestStatus.ACCEPTED:
            raise BadRequestException(
                "Only accepted requests can be converted to projects. "
                f"Current status: {request.status.value}"
            )

        project_doc = {
            "request_id": request_id,
            "created_by": current_user.id,
            "assigned_to": None,
            "title": request.title,
            "description": request.description,
            "priority": "medium",
            "status": ProjectStatus.PENDING.value,
            "notes": None,
        }
        project = await self.project_repo.create(project_doc)

        await self.request_repo.update_status(
            request_id,
            {"status": ProjectRequestStatus.CONVERTED_TO_PROJECT.value}
        )

        await self.update_repo.create({
            "project_id": project.id,
            "updated_by": current_user.id,
            "message": f"Project created from customer request '{request.title}'.",
            "status_changed_to": ProjectStatus.PENDING.value,
            "attachments": [],
        })

        await audit(
            db=self.project_repo.collection.database,
            actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="project_created",
            description=f"Project created from request: \"{project.title}\"",
            entity_type="project", entity_id=project.id,
            metadata={"request_id": request_id},
        )
        await inc_metric(self.project_repo.collection.database, "projects_created")
        return _to_project_response(project)

    async def get_projects(
        self,
        current_user: UserModel,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> PaginatedResponse[ProjectResponse]:
        skip = (page - 1) * page_size

        if is_admin(current_user):
            projects, total = await self.project_repo.find_all(
                status=status, skip=skip, limit=page_size
            )
        else:
            projects, total = await self.project_repo.find_by_associate(
                current_user.id, status=status, skip=skip, limit=page_size
            )

        return PaginatedResponse(
            items=[_to_project_response(p) for p in projects],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    async def get_project(
        self,
        project_id: str,
        current_user: UserModel,
    ) -> ProjectResponse:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundException("Project")
        assert_can_view_project(current_user, project)
        return _to_project_response(project)

    async def assign_associate(
        self,
        project_id: str,
        data: AssignProjectRequest,
        current_user: UserModel,
    ) -> ProjectResponse:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundException("Project")

        if project.status not in [ProjectStatus.PENDING, ProjectStatus.ASSIGNED]:
            raise BadRequestException(
                "Can only assign associates to pending or already-assigned projects."
            )

        project = await self.project_repo.assign_associate(project_id, data.associate_id)

        # Log the assignment in the timeline
        await self.update_repo.create({
            "project_id": project_id,
            "updated_by": current_user.id,
            "message": f"Project assigned to associate ID: {data.associate_id}.",
            "status_changed_to": ProjectStatus.ASSIGNED.value,
            "attachments": [],
        })

        # Notify the assigned associate
        await notify(
            db=self.project_repo.collection.database,
            user_id=data.associate_id,
            type="project_assigned",
            message=f"You have been assigned to project: \"{project.title}\"",
            link=f"/associate/projects/{project_id}",
        )

        await audit(
            db=self.project_repo.collection.database,
            actor_id=current_user.id, actor_name=current_user.name,
            actor_role=current_user.role, action="project_assigned",
            description=f"Project \"{project.title}\" assigned to associate",
            entity_type="project", entity_id=project_id,
            metadata={"associate_id": data.associate_id},
        )
        return _to_project_response(project)

    async def update_status(
        self,
        project_id: str,
        data: UpdateProjectStatusRequest,
        current_user: UserModel,
    ) -> ProjectResponse:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundException("Project")

        if not is_valid_project_transition(project.status, data.status):
            raise InvalidStateTransitionException(
                current=project.status.value,
                attempted=data.status.value,
            )

        update_data = {"status": data.status.value}
        if data.notes:
            update_data["notes"] = data.notes

        project = await self.project_repo.update(project_id, update_data)

        await self.update_repo.create({
            "project_id": project_id,
            "updated_by": current_user.id,
            "message": data.notes or f"Status updated to '{data.status.value}'.",
            "status_changed_to": data.status.value,
            "attachments": [],
        })

        return _to_project_response(project)

    async def add_update(
        self,
        project_id: str,
        data: CreateProjectUpdateRequest,
        current_user: UserModel,
    ) -> ProjectUpdateResponse:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundException("Project")

        assert_can_update_project(current_user, project)

        update_doc = {
            "project_id": project_id,
            "updated_by": current_user.id,
            "message": data.message,
            "status_changed_to": data.status_changed_to.value if data.status_changed_to else None,
            "attachments": data.attachments,
        }

        if data.status_changed_to:
            if not is_valid_project_transition(project.status, data.status_changed_to):
                raise InvalidStateTransitionException(
                    current=project.status.value,
                    attempted=data.status_changed_to.value,
                )
            await self.project_repo.update(project_id, {"status": data.status_changed_to.value})

        update = await self.update_repo.create(update_doc)
        return _to_update_response(update)

    async def get_updates(
        self,
        project_id: str,
        current_user: UserModel,
    ) -> list[ProjectUpdateResponse]:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundException("Project")

        assert_can_view_project(current_user, project)

        updates = await self.update_repo.find_by_project(project_id)
        return [_to_update_response(u) for u in updates]