import { Link } from "react-router-dom"
import { useMyReviews } from "@/shared/hooks/useReviews"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

const CATEGORY_LABELS: Record<string, string> = {
  overall:  "Overall Experience",
  service:  "Customer Service",
  delivery: "Delivery & Fulfilment",
  quality:  "Book Quality",
}

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-400">
      {"⭐".repeat(rating)}
      {"☆".repeat(5 - rating)}
    </span>
  )
}

export function MyReviewsPage() {
  const { data: reviews, isLoading, isError } = useMyReviews()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading your reviews..." />
      </div>
    )
  }

  if (isError) {
    return <EmptyState title="Failed to load reviews" icon={<span className="text-4xl">⚠️</span>} />
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">My Reviews</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {reviews?.length ?? 0} review{reviews?.length !== 1 ? "s" : ""} submitted
          </p>
        </div>
        <Link
          to="/customer/submit-review"
          className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
        >
          + New Review
        </Link>
      </div>

      {reviews?.length === 0 ? (
        <EmptyState
          title="No reviews yet"
          description="Share your experience with Parkash Book Depot."
          icon={<span className="text-4xl">⭐</span>}
          action={
            <Link
              to="/customer/submit-review"
              className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
            >
              Write a Review
            </Link>
          }
        />
      ) : (
        <div className="space-y-4">
          {reviews?.map((review) => (
            <div key={review.id} className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap mb-1">
                    <StarRating rating={review.rating} />
                    <span className="text-xs px-2 py-0.5 bg-muted text-muted-foreground rounded-full capitalize">
                      {CATEGORY_LABELS[review.category] ?? review.category}
                    </span>
                  </div>
                  <p className="text-sm text-foreground mt-2">{review.message}</p>
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