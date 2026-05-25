import type { ProjectRequestStatus, ProjectStatus } from "@/shared/types"

type AnyStatus = ProjectRequestStatus | ProjectStatus

const STATUS_STYLES: Record<AnyStatus, string> = {
  // Project request statuses
  submitted:             "bg-blue-100 text-blue-700",
  under_review:          "bg-yellow-100 text-yellow-700",
  accepted:              "bg-green-100 text-green-700",
  rejected:              "bg-red-100 text-red-700",
  converted_to_project:  "bg-purple-100 text-purple-700",
  // Project statuses
  pending:               "bg-gray-100 text-gray-700",
  assigned:              "bg-blue-100 text-blue-700",
  in_progress:           "bg-yellow-100 text-yellow-700",
  waiting_supplier:      "bg-orange-100 text-orange-700",
  completed:             "bg-green-100 text-green-700",
  cancelled:             "bg-red-100 text-red-700",
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
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
