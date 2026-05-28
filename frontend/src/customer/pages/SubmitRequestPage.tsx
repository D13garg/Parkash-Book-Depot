import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate } from "react-router-dom"
import { useSubmitProjectRequest } from "@/shared/hooks/useProjectRequests"

const schema = z.object({
  title:               z.string().min(3, "Title must be at least 3 characters"),
  description:         z.string().min(10, "Please provide more detail"),
  category:            z.string().min(1, "Select a category"),
  request_type:        z.enum(["project", "other"]),
  requirements:        z.string().optional(),
  quantity:            z.coerce.number().int().positive().optional().or(z.literal("")),
  institution_name:    z.string().optional(),
  institution_address: z.string().optional(),
  contact_phone:       z.string().optional(),
})

type FormData = z.infer<typeof schema>

export function SubmitRequestPage() {
  const navigate = useNavigate()
  const { mutate: submit, isPending, error, isSuccess } = useSubmitProjectRequest()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { request_type: "project" },
  })

  const requestType = watch("request_type")

  const onSubmit = (data: FormData) => {
    submit(
      {
        ...data,
        quantity: data.quantity ? Number(data.quantity) : undefined,
      },
      {
        onSuccess: () => {
          reset()
          setTimeout(() => navigate("/customer/requests"), 1500)
        },
      }
    )
  }

  const errorMessage = error
    ? (error as any)?.response?.data?.detail ?? "Submission failed."
    : null

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Submit a Request</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Tell us what you need and we'll get back to you.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6">
        {isSuccess && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700 text-sm">
            ✅ Request submitted! Redirecting...
          </div>
        )}
        {errorMessage && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">

          {/* Request Type — shown first, drives everything */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Request Type <span className="text-destructive">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-colors
                ${requestType === "project"
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-muted-foreground"
                }`}
              >
                <input
                  {...register("request_type")}
                  type="radio"
                  value="project"
                  className="mt-0.5"
                />
                <div>
                  <p className="font-medium text-foreground text-sm">📂 Project Request</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Bulk orders, institutional supply, custom book requirements
                  </p>
                </div>
              </label>

              <label className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-colors
                ${requestType === "other"
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-muted-foreground"
                }`}
              >
                <input
                  {...register("request_type")}
                  type="radio"
                  value="other"
                  className="mt-0.5"
                />
                <div>
                  <p className="font-medium text-foreground text-sm">💬 Other Request</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    General inquiries, feedback, or anything else
                  </p>
                </div>
              </label>
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Title <span className="text-destructive">*</span>
            </label>
            <input
              {...register("title")}
              placeholder={requestType === "project"
                ? "e.g. Class 10 CBSE Textbooks for 200 students"
                : "e.g. Question about book availability"
              }
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            {errors.title && <p className="mt-1 text-xs text-destructive">{errors.title.message}</p>}
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Category <span className="text-destructive">*</span>
            </label>
            <select
              {...register("category")}
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">Select a category</option>
              {requestType === "project" ? (
                <>
                  <option value="bulk_order">Bulk Order</option>
                  <option value="institutional">Institutional Supply</option>
                  <option value="custom">Custom Requirement</option>
                </>
              ) : (
                <>
                  <option value="inquiry">General Inquiry</option>
                  <option value="feedback">Feedback</option>
                  <option value="complaint">Complaint</option>
                  <option value="other">Other</option>
                </>
              )}
            </select>
            {errors.category && <p className="mt-1 text-xs text-destructive">{errors.category.message}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Description <span className="text-destructive">*</span>
            </label>
            <textarea
              {...register("description")}
              rows={4}
              placeholder="Describe your request in detail..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
            {errors.description && <p className="mt-1 text-xs text-destructive">{errors.description.message}</p>}
          </div>

          {/* Project-only fields */}
          {requestType === "project" && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Quantity <span className="text-muted-foreground font-normal">(optional)</span>
                  </label>
                  <input
                    {...register("quantity")}
                    type="number"
                    min={1}
                    placeholder="e.g. 200"
                    className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Contact Phone <span className="text-muted-foreground font-normal">(optional)</span>
                  </label>
                  <input
                    {...register("contact_phone")}
                    type="tel"
                    placeholder="+91 98765 43210"
                    className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Institution Name <span className="text-muted-foreground font-normal">(optional)</span>
                  </label>
                  <input
                    {...register("institution_name")}
                    placeholder="School / College / Library"
                    className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Institution Address <span className="text-muted-foreground font-normal">(optional)</span>
                  </label>
                  <input
                    {...register("institution_address")}
                    placeholder="City, State"
                    className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  Additional Requirements <span className="text-muted-foreground font-normal">(optional)</span>
                </label>
                <textarea
                  {...register("requirements")}
                  rows={3}
                  placeholder="Specific editions, publishers, or other requirements..."
                  className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                />
              </div>
            </>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 py-2.5 px-4 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              {isPending ? "Submitting..." : "Submit Request"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/customer/requests")}
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