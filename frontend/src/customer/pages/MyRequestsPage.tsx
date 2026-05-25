import { useState } from "react"
import { Link } from "react-router-dom"
import { useProjectRequests } from "@/shared/hooks/useProjectRequests"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

export function MyRequestsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading, isError } = useProjectRequests(page)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading your requests..." />
      </div>
    )
  }

  if (isError) {
    return (
      <EmptyState
        title="Failed to load requests"
        description="Something went wrong. Please try again."
        icon={<span className="text-4xl">⚠️</span>}
      />
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">My Requests</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {data?.total ?? 0} total requests
          </p>
        </div>
        <Link
          to="/customer/submit-request"
          className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
        >
          + New Request
        </Link>
      </div>

      {data?.items.length === 0 ? (
        <EmptyState
          title="No requests yet"
          description="Submit your first project request to get started."
          icon={<span className="text-4xl">📋</span>}
          action={
            <Link
              to="/customer/submit-request"
              className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
            >
              Submit a Request
            </Link>
          }
        />
      ) : (
        <>
          <div className="space-y-3">
            {data?.items.map((req) => (
              <div
                key={req.id}
                className="bg-card border border-border rounded-xl p-5 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="font-semibold text-foreground">{req.title}</h3>
                      <StatusBadge status={req.status} />
                    </div>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {req.description}
                    </p>
                    <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                      <span>📁 {req.category.replace("_", " ")}</span>
                      {req.quantity && <span>📦 Qty: {req.quantity}</span>}
                      {req.institution_name && <span>🏫 {req.institution_name}</span>}
                      <span>📅 {new Date(req.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                {/* Admin notes or rejection reason */}
                {req.admin_notes && (
                  <div className="mt-3 px-3 py-2 bg-muted rounded-lg text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">Admin note: </span>
                    {req.admin_notes}
                  </div>
                )}
                {req.rejection_reason && (
                  <div className="mt-3 px-3 py-2 bg-destructive/10 rounded-lg text-sm text-destructive">
                    <span className="font-medium">Rejection reason: </span>
                    {req.rejection_reason}
                  </div>
                )}
              </div>
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
