import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useProjects } from "@/shared/hooks/useProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

const PRIORITY_STYLES: Record<string, string> = {
  low:    "bg-gray-100 text-gray-600",
  medium: "bg-blue-100 text-blue-600",
  high:   "bg-orange-100 text-orange-600",
  urgent: "bg-red-100 text-red-600",
}

export function AssignedProjectsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState("")

  const { data, isLoading, isError } = useProjects(page, 20, statusFilter || undefined)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading your projects..." />
      </div>
    )
  }

  if (isError) {
    return (
      <EmptyState
        title="Failed to load projects"
        description="Something went wrong. Please try again."
        icon={<span className="text-4xl">⚠️</span>}
      />
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">My Projects</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {data?.total ?? 0} projects assigned to you
          </p>
        </div>

        {/* Status filter */}
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All statuses</option>
          <option value="assigned">Assigned</option>
          <option value="in_progress">In Progress</option>
          <option value="waiting_supplier">Waiting Supplier</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {data?.items.length === 0 ? (
        <EmptyState
          title="No projects assigned"
          description="You have no projects assigned to you yet."
          icon={<span className="text-4xl">📂</span>}
        />
      ) : (
        <>
          <div className="space-y-3">
            {data?.items.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/associate/projects/${project.id}`)}
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
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {project.description}
                    </p>
                    <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                      <span>📅 Created: {new Date(project.created_at).toLocaleDateString()}</span>
                      {project.deadline && (
                        <span className={`font-medium ${new Date(project.deadline) < new Date() ? "text-destructive" : "text-foreground"}`}>
                          ⏰ Due: {new Date(project.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-muted-foreground text-lg">→</span>
                </div>
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
