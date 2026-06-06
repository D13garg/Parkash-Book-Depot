import { useAnalytics } from "@/shared/hooks/useAnalytics"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

// ── Reusable components ───────────────────────────────────────────────────────

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-card border border-border rounded-xl p-5 ${className}`}>
      {children}
    </div>
  )
}

function SectionTitle({ icon, title, subtitle }: { icon: string; title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h3 className="font-semibold text-foreground flex items-center gap-2">
        <span>{icon}</span>{title}
      </h3>
      {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
    </div>
  )
}

function StatCard({ icon, label, value, sub, highlight = false }: {
  icon: string; label: string; value: string | number; sub?: string; highlight?: boolean
}) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xl">{icon}</span>
        {sub && <span className="text-xs text-muted-foreground">{sub}</span>}
      </div>
      <p className={`text-2xl font-bold ${highlight ? "text-destructive" : "text-primary"}`}>
        {value}
      </p>
      <p className="text-xs text-muted-foreground mt-1">{label}</p>
    </Card>
  )
}

function Badge({ label, variant }: { label: string; variant: "warning" | "error" | "success" | "info" }) {
  const styles = {
    warning: "badge-warning",
    error:   "badge-danger",
    success: "badge-success",
    info:    "badge-info",
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${styles[variant]}`}>
      {label}
    </span>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function AdminAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useAnalytics()

  if (isLoading) {
    return <div className="flex items-center justify-center py-32"><LoadingSpinner size="lg" text="Running analytics..." /></div>
  }

  if (isError || !data) {
    return <EmptyState title="Failed to load analytics" icon={<span className="text-4xl">⚠️</span>} />
  }

  const { summary, request_conversion_rate, associate_performance,
          review_metrics, low_stock_books, stale_requests, inactive_projects } = data

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Operational Analytics</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Live business intelligence from your data. Cached for 5 minutes.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 text-sm border border-border rounded-lg hover:bg-muted transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {/* ── Executive Summary ── */}
      <section>
        <SectionTitle icon="📊" title="Executive Summary" subtitle="Platform-wide totals" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <StatCard icon="📋" label="Total Requests"    value={summary.total_requests} />
          <StatCard icon="📂" label="Total Projects"    value={summary.total_projects} />
          <StatCard icon="✅" label="Completed"         value={summary.completed_projects} />
          <StatCard icon="📈" label="Completion Rate"   value={`${summary.completion_rate_percent}%`} />
          <StatCard icon="⭐" label="Total Reviews"     value={summary.total_reviews} />
          <StatCard icon="📦" label="Low Stock Books"   value={summary.low_stock_count}
            highlight={summary.low_stock_count > 0} />
          <StatCard icon="🔴" label="Errors (24h)"      value={summary.error_count_24h}
            highlight={summary.error_count_24h > 0} />
          <StatCard icon="🔄" label="Conversion Rate"   value={`${request_conversion_rate}%`} />
        </div>
      </section>

      {/* ── Request Conversion + Project Performance ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <Card>
          <SectionTitle icon="📋" title="Request Conversion" subtitle="How many requests become projects" />
          <div className="space-y-3">
            <div className="flex items-center justify-between py-3 border-b border-border">
              <span className="text-sm text-muted-foreground">Total Submitted</span>
              <span className="font-semibold text-foreground">{summary.total_requests}</span>
            </div>
            <div className="flex items-center justify-between py-3 border-b border-border">
              <span className="text-sm text-muted-foreground">Converted to Projects</span>
              <span className="font-semibold text-success">{summary.completed_projects}</span>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-sm text-muted-foreground">Conversion Rate</span>
              <span className={`font-bold text-lg ${request_conversion_rate >= 50 ? "text-success" : "text-warning"}`}>
                {request_conversion_rate}%
              </span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all"
                style={{ width: `${Math.min(request_conversion_rate, 100)}%` }}
              />
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle icon="📂" title="Project Performance" subtitle="Completion overview" />
          <div className="space-y-3">
            <div className="flex items-center justify-between py-3 border-b border-border">
              <span className="text-sm text-muted-foreground">Total Projects</span>
              <span className="font-semibold text-foreground">{summary.total_projects}</span>
            </div>
            <div className="flex items-center justify-between py-3 border-b border-border">
              <span className="text-sm text-muted-foreground">Completed</span>
              <span className="font-semibold text-success">{summary.completed_projects}</span>
            </div>
            <div className="flex items-center justify-between py-3 border-b border-border">
              <span className="text-sm text-muted-foreground">In Progress</span>
              <span className="font-semibold text-info">
                {summary.total_projects - summary.completed_projects}
              </span>
            </div>
            <div className="flex items-center justify-between py-3">
              <span className="text-sm text-muted-foreground">Completion Rate</span>
              <span className={`font-bold text-lg ${summary.completion_rate_percent >= 60 ? "text-success" : "text-warning"}`}>
                {summary.completion_rate_percent}%
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* ── Associate Performance ── */}
      <section>
        <SectionTitle icon="👷" title="Associate Performance" subtitle="Per-associate workload and completion stats" />
        {associate_performance.length === 0 ? (
          <Card>
            <p className="text-sm text-muted-foreground text-center py-4">
              No associates found. Create associate accounts to track performance.
            </p>
          </Card>
        ) : (
          <Card className="p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Associate</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Assigned</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Completed</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Open</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Avg Days</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {associate_performance.map((a) => (
                  <tr key={a.associate_id} className="hover:bg-muted/40">
                    <td className="px-4 py-3">
                      <p className="font-medium text-foreground">{a.associate_name}</p>
                      <p className="text-xs text-muted-foreground">{a.associate_email}</p>
                    </td>
                    <td className="px-4 py-3 text-foreground">{a.assigned_projects}</td>
                    <td className="px-4 py-3">
                      <span className="text-success font-medium">{a.completed_projects}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={a.open_projects > 3 ? "text-warning font-medium" : "text-foreground"}>
                        {a.open_projects}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {a.avg_completion_days !== null ? `${a.avg_completion_days}d` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>

      {/* ── Review Metrics + Low Stock ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <Card>
          <SectionTitle icon="⭐" title="Review Metrics" subtitle="Customer satisfaction overview" />
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-primary">
                {review_metrics.average_rating > 0 ? review_metrics.average_rating.toFixed(1) : "—"}
              </div>
              <div>
                <div className="flex gap-0.5">
                  {[1,2,3,4,5].map((s) => (
                    <span key={s} className={s <= Math.round(review_metrics.average_rating) ? "text-primary" : "text-muted-foreground/40"}>
                      ★
                    </span>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">Average rating</p>
              </div>
            </div>
            <div className="space-y-2 pt-2 border-t border-border">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Reviews</span>
                <span className="font-medium">{review_metrics.total_reviews}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">This Month</span>
                <span className="font-medium text-primary">{review_metrics.reviews_this_month}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle icon="📦" title="Low Stock Alert" subtitle="Books below threshold — top 5" />
          {low_stock_books.length === 0 ? (
            <p className="text-sm text-success flex items-center gap-2">
              <span>✅</span> All books are well stocked.
            </p>
          ) : (
            <div className="space-y-3">
              {low_stock_books.map((book) => (
                <div key={book.id} className="flex items-center justify-between">
                  <p className="text-sm text-foreground line-clamp-1 flex-1 mr-3">{book.title}</p>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`text-sm font-bold ${book.stock === 0 ? "text-destructive" : "text-warning"}`}>
                      {book.stock} left
                    </span>
                    <Badge label={book.stock === 0 ? "Out" : "Low"} variant={book.stock === 0 ? "error" : "warning"} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* ── Stale Requests + Inactive Projects ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <Card>
          <SectionTitle icon="⏳" title="Stale Requests" subtitle="Pending for more than 7 days — needs attention" />
          {stale_requests.length === 0 ? (
            <p className="text-sm text-success flex items-center gap-2">
              <span>✅</span> No stale requests.
            </p>
          ) : (
            <div className="space-y-3">
              {stale_requests.map((req) => (
                <div key={req.id} className="flex items-start justify-between gap-3 py-2 border-b border-border last:border-0">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground line-clamp-1">{req.title}</p>
                    <p className="text-xs text-muted-foreground capitalize">{req.category.replace(/_/g, " ")}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge label={req.status.replace(/_/g, " ")} variant="warning" />
                    <span className="text-xs text-destructive font-medium">{req.days_old}d</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <SectionTitle icon="🔄" title="Inactive Projects" subtitle="In progress with no update for 14+ days" />
          {inactive_projects.length === 0 ? (
            <p className="text-sm text-success flex items-center gap-2">
              <span>✅</span> All active projects are being updated.
            </p>
          ) : (
            <div className="space-y-3">
              {inactive_projects.map((proj) => (
                <div key={proj.id} className="flex items-start justify-between gap-3 py-2 border-b border-border last:border-0">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground line-clamp-1">{proj.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {proj.assigned_to ? "Assigned" : "⚠️ Unassigned"}
                    </p>
                  </div>
                  <span className="text-xs text-destructive font-medium flex-shrink-0">
                    {proj.days_since_update}d idle
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

    </div>
  )
}