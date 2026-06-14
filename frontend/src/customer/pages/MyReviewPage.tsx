import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useMyReviews, useUpdateReview, useDeleteReview } from "@/shared/hooks/useReviews"
import type { Review } from "@/shared/types"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

const CATEGORIES = ["Overall Experience", "Service", "Delivery", "Quality", "Other"]

function StarRating({
  value,
  onChange,
  readonly = false,
}: {
  value: number
  onChange?: (v: number) => void
  readonly?: boolean
}) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          onClick={() => onChange?.(star)}
          className={`text-xl transition-transform ${readonly ? "cursor-default" : "hover:scale-110"} ${
            star <= value ? "text-primary" : "text-muted-foreground/30"
          }`}
        >
          ★
        </button>
      ))}
    </div>
  )
}

function ReviewCard({ review }: { review: Review }) {
  const { mutate: updateReview, isPending: isUpdating } = useUpdateReview()
  const { mutate: deleteReview, isPending: isDeleting } = useDeleteReview()

  const [isEditing, setIsEditing] = useState(false)
  const [editRating, setEditRating] = useState(review.rating)
  const [editCategory, setEditCategory] = useState(review.category)
  const [editMessage, setEditMessage] = useState(review.message)

  const handleSave = () => {
    updateReview(
      {
        reviewId: review.id,
        data: { rating: editRating, category: editCategory, message: editMessage },
      },
      { onSuccess: () => setIsEditing(false) }
    )
  }

  const handleDelete = () => {
    if (confirm("Delete this review? This cannot be undone.")) {
      deleteReview(review.id)
    }
  }

  const handleCancel = () => {
    setEditRating(review.rating)
    setEditCategory(review.category)
    setEditMessage(review.message)
    setIsEditing(false)
  }

  // Use the actual stored timestamp, not current time
  const displayDate = new Date(review.created_at).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })

  const wasEdited = review.updated_at && review.updated_at !== review.created_at

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <StarRating value={isEditing ? editRating : review.rating} onChange={isEditing ? setEditRating : undefined} readonly={!isEditing} />
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
              {isEditing ? editCategory : review.category}
            </span>
            <span className="text-xs text-muted-foreground">
              {displayDate}
              {wasEdited && <span className="ml-1 italic">(edited)</span>}
            </span>
          </div>
        </div>

        {/* Action buttons */}
        {!isEditing && (
          <div className="flex gap-2 flex-shrink-0">
            <button
              onClick={() => setIsEditing(true)}
              className="text-xs px-3 py-1.5 rounded-lg border border-input text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-xs px-3 py-1.5 rounded-lg border border-destructive/30 text-destructive hover:bg-destructive/10 disabled:opacity-50 transition-colors"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Category</label>
            <select
              value={editCategory}
              onChange={(e) => setEditCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Message</label>
            <textarea
              value={editMessage}
              onChange={(e) => setEditMessage(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isUpdating || !editMessage.trim()}
              className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {isUpdating ? "Saving..." : "Save changes"}
            </button>
            <button
              onClick={handleCancel}
              disabled={isUpdating}
              className="px-4 py-2 text-sm font-medium border border-input rounded-lg hover:bg-muted/50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-foreground leading-relaxed">{review.message}</p>
      )}
    </div>
  )
}

export function MyReviewsPage() {
  const navigate = useNavigate()
  const { data: reviews, isLoading, isError } = useMyReviews()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <EmptyState title="Failed to load reviews" />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Reviews</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {reviews?.length ?? 0} review{reviews?.length !== 1 ? "s" : ""} submitted
          </p>
        </div>
        <button
          onClick={() => navigate("/customer/submit-review")}
          className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
        >
          + New Review
        </button>
      </div>

      {!reviews?.length ? (
        <EmptyState
          title="No reviews yet"
          description="Share your experience with Parkash Book Depot."
          action={
            <button
              onClick={() => navigate("/customer/submit-review")}
              className="btn-primary mt-4"
            >
              Write a Review
            </button>
          }
        />
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      )}
    </div>
  )
}