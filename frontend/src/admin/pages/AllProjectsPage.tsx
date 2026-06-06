/// <reference types="react" />
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAdminProjects } from "@/shared/hooks/useAdminProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

const PRIORITY_STYLES: Record<string, string> = {
  low:    "badge-neutral",
  medium: "badge-info",
  high:   "badge-warning",
  urgent: "badge-danger",
}

export function AllProjectsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState("")

  const { data, isLoading, isError } = useAdminProjects(page, 20, statusFilter || undefined)

  if (isLoading) {
    return <div className="flex items-center justify-center py-32"><LoadingSpinner size="lg" text="Loading projects..." /></div>
  }

  if (isError) {
    return <EmptyState title="Failed to load projects" icon={<span className="text-4xl">⚠️</span>} />
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">All Projects</h2>
          <p className="text-sm text-muted-foreground mt-1">{data?.total ?? 0} total projects</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="assigned">Assigned</option>
          <option value="in_progress">In Progress</option>
          <option value="waiting_supplier">Waiting Supplier</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {data?.items.length === 0 ? (
        <EmptyState
          title="No projects yet"
          description="Projects are created from accepted customer requests."
          icon={<span className="text-4xl">📂</span>}
        />
      ) : (
        <>
          <div className="space-y-3">
            {data?.items.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/admin/projects/${project.id}`)}
                className="bg-card border border-border rounded-xl p-5 cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="font-semibold text-foreground">{project.title}</h3>
                      <StatusBadge status={project.status} />
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${PRIORITY_STYLES[project.priority] ?? PRIORITY_STYLES.medium}`}>
                        {project.priority}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{project.description}</p>
                    <div className="flex flex-wrap gap-4 mt-3 text-xs text-muted-foreground">
                      <span>📅 {new Date(project.created_at).toLocaleDateString()}</span>
                      {project.assigned_to
                        ? <span className="text-success">👤 Assigned</span>
                        : <span className="text-warning">⚠️ Unassigned</span>
                      }
                      {project.deadline && (
                        <span className={new Date(project.deadline) < new Date() ? "text-destructive font-medium" : ""}>
                          ⏰ Due: {new Date(project.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-muted-foreground">→</span>
                </div>
              </div>
            ))}
          </div>
          <Pagination page={page} totalPages={data?.total_pages ?? 1} onPageChange={setPage} />
        </>
      )}
    </div>
  )
}