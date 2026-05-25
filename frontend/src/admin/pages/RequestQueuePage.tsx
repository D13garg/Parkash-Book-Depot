import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAdminRequests, useUpdateRequestStatus } from "@/shared/hooks/useAdminRequests"
import { useConvertRequestToProject } from "@/shared/hooks/useAdminProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"
import type { ProjectRequest, ProjectRequestStatus } from "@/shared/types"

function RequestActions({ request }: { request: ProjectRequest }) {
  const { mutate: updateStatus, isPending } = useUpdateRequestStatus()
  const { mutate: convert, isPending: isConverting } = useConvertRequestToProject()
  const navigate = useNavigate()
  const [rejectReason, setRejectReason] = useState("")
  const [showReject, setShowReject] = useState(false)

  const act = (status: ProjectRequestStatus, extra?: { admin_notes?: string; rejection_reason?: string }) => {
    updateStatus({ requestId: request.id, status, ...extra })
    setShowReject(false)
    setRejectReason("")
  }

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {request.status === "submitted" && (
        <button
          disabled={isPending}
          onClick={() => act("under_review")}
          className="px-3 py-1.5 text-xs font-medium rounded-lg bg-yellow-100 text-yellow-800 hover:bg-yellow-200 disabled:opacity-50"
        >
          Start Review
        </button>
      )}
      {request.status === "under_review" && (
        <>
          <button
            disabled={isPending}
            onClick={() => act("accepted")}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-green-100 text-green-800 hover:bg-green-200 disabled:opacity-50"
          >
            Accept
          </button>
          <button
            disabled={isPending}
            onClick={() => setShowReject(true)}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-red-100 text-red-800 hover:bg-red-200 disabled:opacity-50"
          >
            Reject
          </button>
        </>
      )}
      {request.status === "accepted" && (
        <button
          disabled={isConverting}
          onClick={() =>
            convert(request.id, {
              onSuccess: (project) => navigate(`/admin/projects/${project.id}`),
            })
          }
          className="px-3 py-1.5 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isConverting ? "Creating..." : "Create Project"}
        </button>
      )}
      {showReject && (
        <div className="w-full flex flex-col sm:flex-row gap-2 mt-2">
          <input
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Rejection reason (required)"
            className="flex-1 px-3 py-2 rounded-lg border border-input bg-background text-sm"
          />
          <button
            disabled={isPending || !rejectReason.trim()}
            onClick={() => act("rejected", { rejection_reason: rejectReason.trim() })}
            className="px-3 py-2 text-xs font-medium rounded-lg bg-destructive text-destructive-foreground disabled:opacity-50"
          >
            Confirm Reject
          </button>
        </div>
      )}
    </div>
  )
}

export function RequestQueuePage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState("")

  const { data, isLoading, isError } = useAdminRequests(page, 20, statusFilter || undefined)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading requests..." />
      </div>
    )
  }

  if (isError) {
    return <EmptyState title="Failed to load requests" icon={<span className="text-4xl">⚠️</span>} />
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Request Queue</h2>
          <p className="text-sm text-muted-foreground mt-1">{data?.total ?? 0} customer requests</p>
        </div>
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
          <option value="converted_to_project">Converted</option>
        </select>
      </div>

      {!data || data.items.length === 0 ? (
        <EmptyState
          title="No requests"
          description="Customer project requests will appear here."
          icon={<span className="text-4xl">📋</span>}
        />
      ) : (
        <>
          <div className="space-y-3">
            {data!.items.map((req) => (
              <div key={req.id} className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="font-semibold text-foreground">{req.title}</h3>
                      <StatusBadge status={req.status} />
                    </div>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{req.description}</p>
                    <div className="flex flex-wrap gap-4 mt-2 text-xs text-muted-foreground">
                      <span>{req.category}</span>
                      {req.institution_name && <span>{req.institution_name}</span>}
                      <span>{new Date(req.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                {req.rejection_reason && (
                  <p className="mt-2 text-sm text-destructive">Rejected: {req.rejection_reason}</p>
                )}
                <RequestActions request={req} />
              </div>
            ))}
          </div>
          <Pagination page={page} totalPages={data?.total_pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  )
}
