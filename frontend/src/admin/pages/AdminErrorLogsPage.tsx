import { useState } from "react"
import { useErrorLogs } from "@/shared/hooks/useErrorLogs.ts"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return "just now"
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export function AdminErrorLogsPage() {
  const [page, setPage] = useState(1)
  const [levelFilter, setLevelFilter] = useState("")
  const [endpointFilter, setEndpointFilter] = useState("")
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data, isLoading, isError } = useErrorLogs({
    page, pageSize: 50,
    level: levelFilter || undefined,
    endpoint: endpointFilter || undefined,
  })

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Error Logs</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Last 7 days of system errors and warnings. Auto-deleted after 7 days.
          {data && ` ${data.total} events.`}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={levelFilter}
          onChange={(e) => { setLevelFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All levels</option>
          <option value="ERROR">ERROR</option>
          <option value="WARNING">WARNING</option>
        </select>

        <input
          value={endpointFilter}
          onChange={(e) => { setEndpointFilter(e.target.value); setPage(1) }}
          placeholder="Filter by endpoint..."
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring w-48"
        />

        {(levelFilter || endpointFilter) && (
          <button
            onClick={() => { setLevelFilter(""); setEndpointFilter(""); setPage(1) }}
            className="px-3 py-2 text-sm text-muted-foreground hover:text-foreground border border-border rounded-lg hover:bg-muted transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-32">
          <LoadingSpinner size="lg" text="Loading error logs..." />
        </div>
      ) : isError ? (
        <EmptyState title="Failed to load error logs" icon={<span className="text-4xl">⚠️</span>} />
      ) : data?.items.length === 0 ? (
        <EmptyState
          title="No errors recorded"
          description="System errors will appear here. Logs auto-delete after 7 days."
          icon={<span className="text-4xl">✅</span>}
        />
      ) : (
        <>
          <div className="space-y-2">
            {data?.items.map((log) => (
              <div
                key={log.id}
                className={`surface-card overflow-hidden transition-all
                  ${log.level === "ERROR" ? "border-destructive/30" : "border-warning/30"}`}
              >
                {/* Main row */}
                <div
                  className="flex items-start gap-3 px-4 py-3 cursor-pointer hover:bg-muted/40"
                  onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                >
                  {/* Level badge */}
                  <span className={`flex-shrink-0 mt-0.5 text-xs font-bold
                    ${log.level === "ERROR" ? "badge-danger" : "badge-warning"}`}
                  >
                    {log.level}
                  </span>

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {log.message}
                    </p>
                    <div className="flex items-center gap-3 mt-0.5 text-xs text-muted-foreground">
                      {log.method && log.endpoint && (
                        <span className="font-mono">{log.method} {log.endpoint}</span>
                      )}
                      {log.status_code && (
                        <span className={`font-medium ${log.status_code >= 500 ? "text-destructive" : "text-warning"}`}>
                          {log.status_code}
                        </span>
                      )}
                      {log.ip_address && <span>IP: {log.ip_address}</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs text-muted-foreground">{timeAgo(log.created_at)}</span>
                    <span className="text-muted-foreground text-xs">
                      {expandedId === log.id ? "▲" : "▼"}
                    </span>
                  </div>
                </div>

                {/* Expanded stack trace */}
                {expandedId === log.id && log.stack_trace && (
                  <div className="px-4 pb-4 border-t border-border">
                    <p className="text-xs font-medium text-muted-foreground mb-2 mt-3">
                      Stack Trace:
                    </p>
                    <pre className="text-xs bg-muted p-3 rounded-lg overflow-x-auto text-foreground whitespace-pre-wrap font-mono">
                      {log.stack_trace}
                    </pre>
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