import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAdminProject, useAdminProjectUpdates, useAssignAssociate, useUpdateProjectStatus } from "@/shared/hooks/useAdminProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import type { ProjectStatus } from "@/shared/types"

const VALID_NEXT_STATUSES: Record<string, ProjectStatus[]> = {
  pending:          ["assigned", "cancelled"],
  assigned:         ["in_progress", "cancelled"],
  in_progress:      ["waiting_supplier", "completed", "cancelled"],
  waiting_supplier: ["in_progress", "cancelled"],
  completed:        [],
  cancelled:        [],
}

export function AdminProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()

  const { data: project, isLoading } = useAdminProject(projectId!)
  const { data: updates, isLoading: updatesLoading } = useAdminProjectUpdates(projectId!)
  const { mutate: assign, isPending: isAssigning } = useAssignAssociate(projectId!)
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateProjectStatus(projectId!)

  const [associateId, setAssociateId] = useState("")
  const [selectedStatus, setSelectedStatus] = useState<ProjectStatus | "">("")
  const [statusNote, setStatusNote] = useState("")

  if (isLoading) {
    return <div className="flex items-center justify-center py-32"><LoadingSpinner size="lg" text="Loading project..." /></div>
  }

  if (!project) {
    return <EmptyState title="Project not found" icon={<span className="text-4xl">❌</span>} />
  }

  const nextStatuses = VALID_NEXT_STATUSES[project.status] ?? []

  return (
    <div className="max-w-3xl space-y-6">
      <button
        onClick={() => navigate("/admin/projects")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
      >
        ← Back to projects
      </button>

      {/* Project info */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h2 className="text-xl font-bold text-foreground">{project.title}</h2>
            <p className="text-sm text-muted-foreground mt-1">{project.description}</p>
          </div>
          <StatusBadge status={project.status} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-5">
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Priority</p>
            <p className="mt-1 text-sm font-medium capitalize">{project.priority}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Assigned To</p>
            <p className="mt-1 text-sm font-medium">
              {project.assigned_to
                ? <span className="text-green-600">ID: {project.assigned_to.slice(-8)}</span>
                : <span className="text-orange-500">Unassigned</span>
              }
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Created</p>
            <p className="mt-1 text-sm">{new Date(project.created_at).toLocaleDateString()}</p>
          </div>
          {project.deadline && (
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">Deadline</p>
              <p className={`mt-1 text-sm font-medium ${new Date(project.deadline) < new Date() ? "text-destructive" : ""}`}>
                {new Date(project.deadline).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Assign associate */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="font-semibold text-foreground mb-4">Assign Associate</h3>
        <div className="flex gap-3">
          <input
            value={associateId}
            onChange={(e) => setAssociateId(e.target.value)}
            placeholder="Paste associate user ID..."
            className="flex-1 px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button
            onClick={() => { if (associateId.trim()) assign(associateId.trim()) }}
            disabled={isAssigning || !associateId.trim()}
            className="px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isAssigning ? "Assigning..." : "Assign"}
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          You can find user IDs in the users collection of your database.
        </p>
      </div>

      {/* Update status */}
      {nextStatuses.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold text-foreground mb-4">Update Status</h3>
          <div className="space-y-3">
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as ProjectStatus)}
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">Select new status...</option>
              {nextStatuses.map((s) => (
                <option key={s} value={s}>{s.replace("_", " ")}</option>
              ))}
            </select>
            <input
              value={statusNote}
              onChange={(e) => setStatusNote(e.target.value)}
              placeholder="Add a note (optional)..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              onClick={() => {
                if (selectedStatus) {
                  updateStatus({ status: selectedStatus, notes: statusNote || undefined })
                  setSelectedStatus("")
                  setStatusNote("")
                }
              }}
              disabled={isUpdatingStatus || !selectedStatus}
              className="px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {isUpdatingStatus ? "Updating..." : "Update Status"}
            </button>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div>
        <h3 className="text-lg font-semibold text-foreground mb-4">Project Timeline</h3>
        {updatesLoading ? (
          <LoadingSpinner size="sm" />
        ) : updates?.length === 0 ? (
          <EmptyState title="No updates yet" icon={<span className="text-3xl">🕐</span>} />
        ) : (
          <div className="relative space-y-0">
            <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-border" />
            {updates?.map((update, index) => (
              <div key={update.id} className="relative flex gap-4 pb-6">
                <div className={`relative z-10 flex-shrink-0 h-8 w-8 rounded-full border-2 flex items-center justify-center text-xs
                  ${index === (updates.length - 1) ? "bg-primary border-primary text-primary-foreground" : "bg-card border-border text-muted-foreground"}`}
                >
                  {update.status_changed_to ? "🔄" : "💬"}
                </div>
                <div className="flex-1 bg-card border border-border rounded-xl p-4">
                  <div className="flex items-center justify-between gap-2 flex-wrap mb-2">
                    {update.status_changed_to && <StatusBadge status={update.status_changed_to} />}
                    <span className="text-xs text-muted-foreground">{new Date(update.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-sm text-foreground">{update.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}