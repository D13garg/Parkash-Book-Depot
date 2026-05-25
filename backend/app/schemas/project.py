from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.enums import ProjectStatus


# ── Project request schemas ────────────────────────────────────────────────────

class AssignProjectRequest(BaseModel):
    associate_id: str


class UpdateProjectStatusRequest(BaseModel):
    status: ProjectStatus
    notes: Optional[str] = None


# ── Project update (timeline entry) request schemas ───────────────────────────

class CreateProjectUpdateRequest(BaseModel):
    message: str = Field(..., min_length=1)
    status_changed_to: Optional[ProjectStatus] = None
    attachments: List[str] = []


# ── Response schemas ───────────────────────────────────────────────────────────

class ProjectResponse(BaseModel):
    id: str
    request_id: str
    created_by: str
    assigned_to: Optional[str] = None
    title: str
    description: str
    priority: str
    deadline: Optional[datetime] = None
    status: ProjectStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProjectUpdateResponse(BaseModel):
    id: str
    project_id: str
    updated_by: str
    message: str
    status_changed_to: Optional[ProjectStatus] = None
    attachments: List[str]
    created_at: datetime
