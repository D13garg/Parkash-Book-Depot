import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate } from "react-router-dom"
import { useSubmitReview } from "@/shared/hooks/useReviews"

const schema = z.object({
  rating:   z.number().min(1).max(5),
  category: z.string().min(1, "Select a category"),
  message:  z.string().min(5, "Please write at least 5 characters"),
})

type FormData = z.infer<typeof schema>

export function SubmitReviewPage() {
  const navigate = useNavigate()
  const { mutate: submit, isPending, isSuccess, error } = useSubmitReview()

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { rating: 5, category: "" },
  })

  const currentRating = watch("rating")

  const onSubmit = (data: FormData) => {
    submit(data, {
      onSuccess: () => setTimeout(() => navigate("/customer/reviews"), 1500),
    })
  }

  const errorMessage = error
    ? (error as any)?.response?.data?.detail ?? "Failed to submit review."
    : null

  return (
    <div className="max-w-xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Submit a Review</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Share your experience with Parkash Book Depot.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6">
        {isSuccess && (
          <div className="mb-4 alert-success">
            ✅ Review submitted! Redirecting...
          </div>
        )}
        {errorMessage && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">

          {/* Rating — star buttons */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Rating <span className="text-destructive">*</span>
            </label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setValue("rating", star)}
                  className={`text-2xl transition-transform hover:scale-110 ${
                    star <= currentRating ? "text-primary" : "text-muted-foreground/40"
                  }`}
                >
                  ★
                </button>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {currentRating === 5 ? "Excellent" :
               currentRating === 4 ? "Good" :
               currentRating === 3 ? "Average" :
               currentRating === 2 ? "Poor" : "Very Poor"}
            </p>
            {errors.rating && <p className="mt-1 text-xs text-destructive">{errors.rating.message}</p>}
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
              <option value="overall">Overall Experience</option>
              <option value="service">Customer Service</option>
              <option value="delivery">Delivery & Fulfilment</option>
              <option value="quality">Book Quality</option>
            </select>
            {errors.category && <p className="mt-1 text-xs text-destructive">{errors.category.message}</p>}
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Your Review <span className="text-destructive">*</span>
            </label>
            <textarea
              {...register("message")}
              rows={5}
              placeholder="Tell us about your experience..."
              className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
            {errors.message && <p className="mt-1 text-xs text-destructive">{errors.message.message}</p>}
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 py-2.5 px-4 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              {isPending ? "Submitting..." : "Submit Review"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/customer/reviews")}
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