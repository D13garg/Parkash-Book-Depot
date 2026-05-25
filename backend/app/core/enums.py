from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ASSOCIATE = "associate"
    ADMIN = "admin"


class ProjectRequestStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONVERTED_TO_PROJECT = "converted_to_project"


class ProjectStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_SUPPLIER = "waiting_supplier"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ── Valid state transitions (state machine rules) ─────────────────────────────

PROJECT_REQUEST_TRANSITIONS: dict[ProjectRequestStatus, list[ProjectRequestStatus]] = {
    ProjectRequestStatus.SUBMITTED: [ProjectRequestStatus.UNDER_REVIEW],
    ProjectRequestStatus.UNDER_REVIEW: [
        ProjectRequestStatus.ACCEPTED,
        ProjectRequestStatus.REJECTED,
    ],
    ProjectRequestStatus.ACCEPTED: [ProjectRequestStatus.CONVERTED_TO_PROJECT],
    ProjectRequestStatus.REJECTED: [],
    ProjectRequestStatus.CONVERTED_TO_PROJECT: [],
}

PROJECT_TRANSITIONS: dict[ProjectStatus, list[ProjectStatus]] = {
    ProjectStatus.PENDING: [ProjectStatus.ASSIGNED, ProjectStatus.CANCELLED],
    ProjectStatus.ASSIGNED: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
    ProjectStatus.IN_PROGRESS: [
        ProjectStatus.WAITING_SUPPLIER,
        ProjectStatus.COMPLETED,
        ProjectStatus.CANCELLED,
    ],
    ProjectStatus.WAITING_SUPPLIER: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
    ProjectStatus.COMPLETED: [],
    ProjectStatus.CANCELLED: [],
}


def is_valid_request_transition(current: ProjectRequestStatus, next_status: ProjectRequestStatus) -> bool:
    return next_status in PROJECT_REQUEST_TRANSITIONS.get(current, [])


def is_valid_project_transition(current: ProjectStatus, next_status: ProjectStatus) -> bool:
    return next_status in PROJECT_TRANSITIONS.get(current, [])
