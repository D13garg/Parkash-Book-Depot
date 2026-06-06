import { useAllReviews } from "@/shared/hooks/useReviews"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

const CATEGORY_LABELS: Record<string, string> = {
  overall:  "Overall Experience",
  service:  "Customer Service",
  delivery: "Delivery & Fulfilment",
  quality:  "Book Quality",
}

function StarRating({ rating }: { rating: number }) {
  return <span className="text-primary">{"⭐".repeat(rating)}{"☆".repeat(5 - rating)}</span>
}

export function AdminReviewsPage() {
  const { data: reviews, isLoading, isError } = useAllReviews()

  if (isLoading) {
    return <div className="flex items-center justify-center py-32"><LoadingSpinner size="lg" text="Loading reviews..." /></div>
  }

  if (isError) {
    return <EmptyState title="Failed to load reviews" icon={<span className="text-4xl">⚠️</span>} />
  }

  const avgRating = reviews && reviews.length > 0
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : null

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Customer Reviews</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {reviews?.length ?? 0} total reviews
            {avgRating && <span className="ml-2 text-primary font-medium">⭐ {avgRating} avg</span>}
          </p>
        </div>
      </div>

      {reviews?.length === 0 ? (
        <EmptyState title="No reviews yet" icon={<span className="text-4xl">⭐</span>} />
      ) : (
        <div className="space-y-4">
          {reviews?.map((review) => (
            <div key={review.id} className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap mb-2">
                    <span className="font-semibold text-foreground">{review.customer_name}</span>
                    <StarRating rating={review.rating} />
                    <span className="text-xs px-2 py-0.5 bg-muted text-muted-foreground rounded-full">
                      {CATEGORY_LABELS[review.category] ?? review.category}
                    </span>
                  </div>
                  <p className="text-sm text-foreground">{review.message}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Customer ID: {review.customer_id}
                  </p>
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}