import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useParams, useNavigate } from "react-router-dom"
import { useProject, useAddProjectUpdate } from "@/shared/hooks/useProjects"
import { StatusBadge } from "@/shared/components/StatusBadge"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import type { ProjectStatus } from "@/shared/types"

const schema = z.object({
  message:           z.string().min(1, "Update message is required"),
  status_changed_to: z.string().optional(),
})

type FormData = z.infer<typeof schema>

// Only these transitions make sense for an associate to trigger
const ASSOCIATE_STATUS_OPTIONS: { value: ProjectStatus; label: string }[] = [
  { value: "in_progress",      label: "In Progress" },
  { value: "waiting_supplier", label: "Waiting for Supplier" },
  { value: "completed",        label: "Completed" },
]

export function AddUpdatePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()

  const { data: project, isLoading } = useProject(projectId!)
  const { mutate: addUpdate, isPending, error, isSuccess } = useAddProjectUpdate(projectId!)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = (data: FormData) => {
    addUpdate(
      {
        message: data.message,
        status_changed_to: (data.status_changed_to as ProjectStatus) || undefined,
      },
      {
        onSuccess: () => {
          setTimeout(() => navigate(`/associate/projects/${projectId}`), 1000)
        },
      }
    )
  }

  const errorMessage = error
    ? (error as any)?.response?.data?.detail ?? "Failed to add update."
    : null

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading project..." />
      </div>
    )
  }

  return (
    <div className="max-w-xl">
      {/* Back */}
      <button
        onClick={() => navigate(`/associate/projects/${projectId}`)}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 mb-6 transition-colors"
      >
        ← Back to project
      </button>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Add Update</h2>
        {project && (
          <div className="flex items-center gap-2 mt-1">
            <p className="text-sm text-muted-foreground">{project.title}</p>
            <StatusBadge status={project.status} />
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-xl p-6">
        {isSuccess && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700 text-sm">
            ✅ Update added. Redirecting...
          </div>
        )}

        {errorMessage && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Update Message <span className="text-destructive">*</span>
            </label>
            <textarea
              {...register("message")}
              rows={5}
              placeholder="Describe what you've done, any blockers, or next steps..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
            {errors.message && (
              <p className="mt-1 text-xs text-destructive">{errors.message.message}</p>
            )}
          </div>

          {/* Optional status change */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Change Status{" "}
              <span className="text-muted-foreground font-normal">(optional)</span>
            </label>
            <select
              {...register("status_changed_to")}
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">Keep current status</option>
              {ASSOCIATE_STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-muted-foreground">
              Only select this if the project status has actually changed.
            </p>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 py-2.5 px-4 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {isPending ? "Submitting..." : "Add Update"}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/associate/projects/${projectId}`)}
              className="px-4 py-2.5 text-sm border border-border rounded-lg hover:bg-muted transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
