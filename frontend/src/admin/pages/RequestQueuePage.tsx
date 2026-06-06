import { useState } from "react"
import { useAdminRequests, useUpdateRequestStatus, useConvertToProject } from "@/shared/hooks/useAdminRequests"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"
import type { ProjectRequest } from "@/shared/types"

function RequestCard({
  request,
  onStatusChange,
  onConvert,
  isUpdating,
  isConverting,
}: {
  request: ProjectRequest
  onStatusChange: (status: string, notes?: string, reason?: string) => void
  onConvert: () => void
  isUpdating: boolean
  isConverting: boolean
}) {
  const [showRejectForm, setShowRejectForm] = useState(false)
  const [rejectReason, setRejectReason] = useState("")
  const [adminNote, setAdminNote] = useState("")

  return (
    <div className="surface-card p-5">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h3 className="font-semibold text-foreground">{request.title}</h3>
            <StatusBadge status={request.status} />
          </div>
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
            {request.description}
          </p>
          <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted-foreground">
            <span>📁 {request.category.replace(/_/g, " ")}</span>
            {request.quantity && <span>📦 Qty: {request.quantity}</span>}
            {request.institution_name && <span>🏫 {request.institution_name}</span>}
            {request.contact_phone && <span>📞 {request.contact_phone}</span>}
            <span>📅 {new Date(request.created_at).toLocaleDateString()}</span>
          </div>
          {request.requirements && (
            <p className="mt-2 text-xs text-muted-foreground bg-muted px-3 py-2 rounded-lg">
              <span className="font-medium text-foreground">Requirements: </span>
              {request.requirements}
            </p>
          )}
        </div>
      </div>

      {/* Admin actions */}
      {(request.status === "submitted" || request.status === "under_review") && (
        <div className="mt-4 pt-4 border-t border-border space-y-3">
          <input
            value={adminNote}
            onChange={(e) => setAdminNote(e.target.value)}
            placeholder="Add an admin note (optional)..."
            className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {!showRejectForm ? (
            <div className="flex flex-wrap gap-2">
              {request.status === "submitted" && (
                <button
                  onClick={() => onStatusChange("under_review", adminNote)}
                  disabled={isUpdating}
                  className="btn-warning"
                >
                  Mark Under Review
                </button>
              )}
              {request.status === "under_review" && (
                <button
                  onClick={() => onStatusChange("accepted", adminNote)}
                  disabled={isUpdating}
                  className="btn-success"
                >
                  ✓ Accept
                </button>
              )}
              <button
                onClick={() => setShowRejectForm(true)}
                disabled={isUpdating}
                className="btn-danger"
              >
                ✗ Reject
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Rejection reason (required)..."
                rows={2}
                className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => onStatusChange("rejected", adminNote, rejectReason)}
                  disabled={isUpdating || !rejectReason.trim()}
                  className="btn-danger"
                >
                  Confirm Reject
                </button>
                <button
                  onClick={() => setShowRejectForm(false)}
                  className="px-3 py-1.5 text-sm border border-border rounded-lg hover:bg-muted transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Convert to project — only for project type */}
      {request.status === "accepted" && request.request_type === "project" && (
        <div className="mt-4 pt-4 border-t border-border">
          <button
            onClick={onConvert}
            disabled={isConverting}
            className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isConverting ? "Converting..." : "→ Convert to Project"}
          </button>
        </div>
      )}

      {request.status === "converted_to_project" && (
        <div className="mt-4 pt-4 border-t border-border">
          <span className="text-sm text-purple font-medium">
            ✓ Converted to internal project
          </span>
        </div>
      )}
    </div>
  )
}


export function RequestQueuePage() {
  // "project" tab or "other" tab
  const [activeTab, setActiveTab] = useState<"project" | "other">("project")
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState("")

  const { data, isLoading, isError } = useAdminRequests(
    page, 20, statusFilter || undefined, activeTab
  )
  const { mutate: updateStatus, isPending: isUpdating } = useUpdateRequestStatus()
  const { mutate: convertToProject, isPending: isConverting } = useConvertToProject()

  const handleTabChange = (tab: "project" | "other") => {
    setActiveTab(tab)
    setPage(1)
    setStatusFilter("")
  }

  if (isError) {
    return <EmptyState title="Failed to load requests" icon={<span className="text-4xl">⚠️</span>} />
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Request Queue</h2>
        <p className="text-sm text-muted-foreground mt-1">
          {data?.total ?? 0} requests in this section
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-xl mb-6 w-fit">
        <button
          onClick={() => handleTabChange("project")}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors
            ${activeTab === "project"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
            }`}
        >
          📂 Project Requests
        </button>
        <button
          onClick={() => handleTabChange("other")}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors
            ${activeTab === "other"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
            }`}
        >
          💬 Other Requests
        </button>
      </div>

      {/* Status filter */}
      <div className="flex justify-end mb-4">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All statuses</option>
          <option value="submitted">Submitted</option>
          <option value="under_review">Under Review</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          {activeTab === "project" && (
            <option value="converted_to_project">Converted</option>
          )}
        </select>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-32">
          <LoadingSpinner size="lg" text="Loading requests..." />
        </div>
      ) : data?.items.length === 0 ? (
        <EmptyState
          title={`No ${activeTab === "project" ? "project" : "other"} requests`}
          description={activeTab === "project"
            ? "No bulk orders or institutional requests yet."
            : "No general inquiries or other requests yet."
          }
          icon={<span className="text-4xl">{activeTab === "project" ? "📂" : "💬"}</span>}
        />
      ) : (
        <>
          <div className="space-y-4">
            {data?.items.map((req) => (
              <RequestCard
                key={req.id}
                request={req}
                isUpdating={isUpdating}
                isConverting={isConverting}
                onStatusChange={(status, notes, reason) =>
                  updateStatus({
                    requestId: req.id,
                    status: status as any,
                    admin_notes: notes,
                    rejection_reason: reason,
                  })
                }
                onConvert={() => convertToProject(req.id)}
              />
            ))}
          </div>
          <Pagination
            page={page}
            totalPages={data?.total_pages ?? 1}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}