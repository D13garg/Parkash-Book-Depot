import type { ProjectRequestStatus, ProjectStatus } from "@/shared/types"

type AnyStatus = ProjectRequestStatus | ProjectStatus

const STATUS_STYLES: Record<AnyStatus, string> = {
  submitted:             "badge-info",
  under_review:          "badge-warning",
  accepted:              "badge-success",
  rejected:              "badge-danger",
  converted_to_project:  "badge-purple",
  pending:               "badge-neutral",
  assigned:              "badge-info",
  in_progress:           "badge-warning",
  waiting_supplier:      "badge-warning",
  completed:             "badge-success",
  cancelled:             "badge-danger",
}

const STATUS_LABELS: Record<AnyStatus, string> = {
  submitted:             "Submitted",
  under_review:          "Under Review",
  accepted:              "Accepted",
  rejected:              "Rejected",
  converted_to_project:  "In Progress",
  pending:               "Pending",
  assigned:              "Assigned",
  in_progress:           "In Progress",
  waiting_supplier:      "Waiting Supplier",
  completed:             "Completed",
  cancelled:             "Cancelled",
}

interface StatusBadgeProps {
  status: AnyStatus
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center ${STATUS_STYLES[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  )
}
