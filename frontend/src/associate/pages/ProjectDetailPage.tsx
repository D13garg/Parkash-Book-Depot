import { useParams, useNavigate } from "react-router-dom"
import { useProject, useProjectUpdates } from "@/shared/hooks/useProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()

  const { data: project, isLoading: projectLoading } = useProject(projectId!)
  const { data: updates, isLoading: updatesLoading } = useProjectUpdates(projectId!)

  if (projectLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading project..." />
      </div>
    )
  }

  if (!project) {
    return (
      <EmptyState
        title="Project not found"
        icon={<span className="text-4xl">❌</span>}
      />
    )
  }

  return (
    <div className="max-w-3xl space-y-6">

      {/* Back button */}
      <button
        onClick={() => navigate("/associate/projects")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
      >
        ← Back to projects
      </button>

      {/* Project info card */}
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
            <p className="mt-1 text-sm font-medium capitalize text-foreground">{project.priority}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Created</p>
            <p className="mt-1 text-sm text-foreground">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
          {project.deadline && (
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">Deadline</p>
              <p className={`mt-1 text-sm font-medium ${new Date(project.deadline) < new Date() ? "text-destructive" : "text-foreground"}`}>
                {new Date(project.deadline).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>

        {project.notes && (
          <div className="mt-4 px-4 py-3 bg-muted rounded-lg">
            <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Admin Notes</p>
            <p className="text-sm text-foreground">{project.notes}</p>
          </div>
        )}

        {/* Add update button */}
        <div className="mt-5 pt-5 border-t border-border">
          <button
            onClick={() => navigate(`/associate/projects/${project.id}/add-update`)}
            className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
          >
            + Add Update
          </button>
        </div>
      </div>

      {/* Timeline */}
      <div>
        <h3 className="text-lg font-semibold text-foreground mb-4">Project Timeline</h3>

        {updatesLoading ? (
          <LoadingSpinner size="sm" text="Loading timeline..." />
        ) : updates?.length === 0 ? (
          <EmptyState
            title="No updates yet"
            description="Add the first update to start the project timeline."
            icon={<span className="text-3xl">🕐</span>}
          />
        ) : (
          <div className="relative space-y-0">
            {/* Vertical line */}
            <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-border" />

            {updates?.map((update, index) => (
              <div key={update.id} className="relative flex gap-4 pb-6">
                {/* Dot */}
                <div className={`relative z-10 flex-shrink-0 h-8 w-8 rounded-full border-2 flex items-center justify-center text-xs
                  ${index === (updates.length - 1)
                    ? "bg-primary border-primary text-primary-foreground"
                    : "bg-card border-border text-muted-foreground"
                  }`}
                >
                  {update.status_changed_to ? "🔄" : "💬"}
                </div>

                {/* Content */}
                <div className="flex-1 bg-card border border-border rounded-xl p-4 min-w-0">
                  <div className="flex items-center justify-between gap-2 flex-wrap mb-2">
                    <div className="flex items-center gap-2">
                      {update.status_changed_to && (
                        <StatusBadge status={update.status_changed_to} />
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(update.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-foreground">{update.message}</p>
                  {update.attachments.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {update.attachments.map((url, i) => (
                        <a
                          key={i}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline"
                        >
                          📎 Attachment {i + 1}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
