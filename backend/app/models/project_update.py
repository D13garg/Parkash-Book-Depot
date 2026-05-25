from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from app.core.enums import ProjectStatus


class ProjectUpdateModel(BaseModel):
    """
    A single timeline entry on a project.
    Every status change or note added by admin/associate is stored here.
    Builds a full audit trail of the project's history.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str                          # references projects._id
    updated_by: str                          # user id of who added this update
    message: str                             # the update note/comment
    status_changed_to: Optional[ProjectStatus] = None   # if this update changed the status
    attachments: List[str] = []              # file URLs / references
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
