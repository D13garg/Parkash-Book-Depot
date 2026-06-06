import { useMetricsSummary, useMetricsTrend } from "@/shared/hooks/useMetrics"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, BarChart, Bar
} from "recharts"

// ── Stat card ─────────────────────────────────────────────────
function StatCard({
  label, value, sub, color = "text-primary", icon,
}: {
  label: string
  value: number
  sub?: string
  color?: string
  icon: string
}) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        {sub && <span className="text-xs text-muted-foreground">{sub}</span>}
      </div>
      <p className={`text-3xl font-bold ${color}`}>{value.toLocaleString()}</p>
      <p className="text-sm text-muted-foreground mt-1">{label}</p>
    </div>
  )
}

// ── Section header ────────────────────────────────────────────
function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-4">
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground">{subtitle}</p>
    </div>
  )
}

// ── Chart helper — aggregate hourly → daily ───────────────────
function toDailyData(hourly: any[]) {
  const days: Record<string, any> = {}
  hourly.forEach((h) => {
    const day = new Date(h.hour).toLocaleDateString("en-IN", { month: "short", day: "numeric" })
    if (!days[day]) {
      days[day] = {
        day,
        logins: 0, new_users: 0,
        requests: 0, reviews: 0, errors: 0,
      }
    }
    days[day].logins     += h.logins_success
    days[day].new_users  += h.new_users
    days[day].requests   += h.requests_submitted
    days[day].reviews    += h.reviews_submitted
    days[day].errors     += h.errors_count
  })
  return Object.values(days).slice(-14) // last 14 days
}

export function AdminMetricsDashboard() {
  const { data: summary, isLoading: summaryLoading } = useMetricsSummary()
  const { data: trend, isLoading: trendLoading } = useMetricsTrend()

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading metrics..." />
      </div>
    )
  }

  const dailyData = trend ? toDailyData(trend) : []

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Metrics Dashboard</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Live aggregated data. Refreshes every minute.
        </p>
      </div>

      {/* ── All-time totals ── */}
      <div>
        <SectionHeader title="All Time" subtitle="Total counts across the entire platform" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatCard icon="👥" label="Total Users"    value={summary?.total_users ?? 0}    color="text-info" />
          <StatCard icon="📚" label="Total Books"    value={summary?.total_books ?? 0}    color="text-success" />
          <StatCard icon="📋" label="Total Requests" value={summary?.total_requests ?? 0} color="text-purple" />
          <StatCard icon="📂" label="Total Projects" value={summary?.total_projects ?? 0} color="text-warning" />
          <StatCard icon="⭐" label="Total Reviews"  value={summary?.total_reviews ?? 0}  color="text-primary" />
        </div>
      </div>

      {/* ── Today ── */}
      <div>
        <SectionHeader title="Today" subtitle="Activity in the last 24 hours" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard icon="👤" label="New Users"      value={summary?.today_new_users ?? 0}     sub="today" />
          <StatCard icon="🔑" label="Logins"         value={summary?.today_logins ?? 0}         sub="today" />
          <StatCard icon="🔒" label="Failed Logins"  value={summary?.today_failed_logins ?? 0}  sub="today" color={summary?.today_failed_logins ? "text-warning" : "text-primary"} />
          <StatCard icon="📋" label="Requests"       value={summary?.today_requests ?? 0}       sub="today" />
          <StatCard icon="⭐" label="Reviews"        value={summary?.today_reviews ?? 0}        sub="today" />
          <StatCard icon="🔴" label="Errors"         value={summary?.today_errors ?? 0}         sub="today" color={summary?.today_errors ? "text-destructive" : "text-primary"} />
        </div>
      </div>

      {/* ── This week ── */}
      <div>
        <SectionHeader title="This Week" subtitle="Last 7 days" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatCard icon="👤" label="New Users"  value={summary?.week_new_users ?? 0}  sub="7 days" />
          <StatCard icon="🔑" label="Logins"     value={summary?.week_logins ?? 0}     sub="7 days" />
          <StatCard icon="📋" label="Requests"   value={summary?.week_requests ?? 0}   sub="7 days" />
          <StatCard icon="⭐" label="Reviews"    value={summary?.week_reviews ?? 0}    sub="7 days" />
          <StatCard icon="🔴" label="Errors"     value={summary?.week_errors ?? 0}     sub="7 days" color={summary?.week_errors ? "text-destructive" : "text-primary"} />
        </div>
      </div>

      {/* ── Charts ── */}
      {trendLoading ? (
        <div className="flex items-center justify-center py-16">
          <LoadingSpinner size="md" text="Loading trend data..." />
        </div>
      ) : dailyData.length === 0 ? (
        <div className="surface-card p-8 text-center text-muted-foreground text-sm">
          Not enough data yet for trend charts. Charts will appear after a few days of activity.
        </div>
      ) : (
        <>
          {/* Activity chart */}
          <div className="surface-card p-6">
            <SectionHeader
              title="Activity Trend — Last 14 Days"
              subtitle="Daily logins, requests and reviews"
            />
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: 12,
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="logins"   name="Logins"   stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="requests" name="Requests" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="reviews"  name="Reviews"  stroke="#f59e0b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* New users + errors chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="surface-card p-6">
              <SectionHeader title="New Users" subtitle="Daily registrations" />
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="day" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                  <YAxis tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="new_users" name="New Users" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="surface-card p-6">
              <SectionHeader title="Errors" subtitle="Daily error count" />
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="day" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                  <YAxis tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="errors" name="Errors" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  )
}