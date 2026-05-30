import { useState } from "react"
import { useAuditLogs } from "@/shared/hooks/useAuditLogs"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

const ACTION_ICONS: Record<string, string> = {
  user_registered:        "👤",
  user_login_failed:      "🔒",
  book_created:           "📚",
  book_updated:           "✏️",
  book_deleted:           "🗑️",
  book_stock_updated:     "📦",
  request_submitted:      "📋",
  request_status_changed: "🔄",
  project_created:        "📂",
  project_assigned:       "👷",
  project_status_changed: "🔄",
  review_submitted:       "⭐",
  gallery_photo_uploaded: "🖼️",
  gallery_photo_deleted:  "🗑️",
  gallery_caption_updated:"✏️",
}

const ACTION_COLORS: Record<string, string> = {
  user_registered:        "text-green-600 bg-green-50",
  user_login_failed:      "text-red-600 bg-red-50",
  book_deleted:           "text-red-600 bg-red-50",
  gallery_photo_deleted:  "text-red-600 bg-red-50",
  book_created:           "text-blue-600 bg-blue-50",
  project_created:        "text-blue-600 bg-blue-50",
  gallery_photo_uploaded: "text-blue-600 bg-blue-50",
  project_assigned:       "text-purple-600 bg-purple-50",
  review_submitted:       "text-yellow-600 bg-yellow-50",
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return "just now"
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

const ACTION_OPTIONS = [
  "user_registered", "user_login_failed",
  "book_created", "book_updated", "book_deleted", "book_stock_updated",
  "request_submitted", "request_status_changed",
  "project_created", "project_assigned", "project_status_changed",
  "review_submitted", "gallery_photo_uploaded", "gallery_photo_deleted",
]

const ENTITY_OPTIONS = ["user", "book", "project_request", "project", "gallery"]

export function AdminAuditLogsPage() {
  const [page, setPage] = useState(1)
  const [actionFilter, setActionFilter] = useState("")
  const [entityFilter, setEntityFilter] = useState("")

  const { data, isLoading, isError } = useAuditLogs({
    page, pageSize: 50,
    action: actionFilter || undefined,
    entityType: entityFilter || undefined,
  })

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Activity Logs</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Complete audit trail of all important actions.
          {data && ` ${data.total} total events recorded.`}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All actions</option>
          {ACTION_OPTIONS.map((a) => (
            <option key={a} value={a}>{a.replace(/_/g, " ")}</option>
          ))}
        </select>

        <select
          value={entityFilter}
          onChange={(e) => { setEntityFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All entities</option>
          {ENTITY_OPTIONS.map((e) => (
            <option key={e} value={e}>{e.replace(/_/g, " ")}</option>
          ))}
        </select>

        {(actionFilter || entityFilter) && (
          <button
            onClick={() => { setActionFilter(""); setEntityFilter(""); setPage(1) }}
            className="px-3 py-2 text-sm text-muted-foreground hover:text-foreground border border-border rounded-lg hover:bg-muted transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-32">
          <LoadingSpinner size="lg" text="Loading activity logs..." />
        </div>
      ) : isError ? (
        <EmptyState title="Failed to load logs" icon={<span className="text-4xl">⚠️</span>} />
      ) : data?.items.length === 0 ? (
        <EmptyState
          title="No activity yet"
          description="Actions will appear here as users interact with the system."
          icon={<span className="text-4xl">📋</span>}
        />
      ) : (
        <>
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Action</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Description</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actor</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Entity</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data?.items.map((log) => (
                  <tr key={log.id} className="hover:bg-muted/40 transition-colors">
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${ACTION_COLORS[log.action] ?? "text-gray-600 bg-gray-50"}`}>
                        <span>{ACTION_ICONS[log.action] ?? "🔔"}</span>
                        {log.action.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-foreground max-w-xs">
                      <p className="truncate">{log.description}</p>
                      {log.metadata && Object.keys(log.metadata).length > 0 && (
                        <p className="text-xs text-muted-foreground mt-0.5 truncate">
                          {Object.entries(log.metadata)
                            .filter(([_, v]) => v !== null && v !== undefined)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(" · ")}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-foreground">{log.actor_name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{log.actor_role}</p>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      {log.entity_type && (
                        <span className="px-2 py-0.5 bg-muted rounded-full capitalize">
                          {log.entity_type.replace(/_/g, " ")}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground text-xs whitespace-nowrap">
                      {timeAgo(log.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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