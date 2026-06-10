import { useCartStore } from "@/stores/cartStore"
import type { Book } from "@/shared/types"

interface BookDetailPanelProps {
  book: Book | null
  isOpen: boolean
  onClose: () => void
}

export function BookDetailPanel({ book, isOpen, onClose }: BookDetailPanelProps) {
  const { addItem } = useCartStore()

  if (!book) return null

  const handleAddToCart = () => {
    addItem({
      book_id: book.id,
      title: book.title,
      price: book.price,
      stock: book.stock,
      cover_image_url: book.cover_image_url,
    })
    onClose()
  }

  return (
    <div className={`fixed inset-0 z-50 transition-opacity ${isOpen ? "opacity-100" : "opacity-0 pointer-events-none"}`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div
        className={`absolute right-0 top-0 bottom-0 w-full sm:w-96 bg-background border-l border-border shadow-lg transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        } overflow-y-auto`}
      >
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between p-4 border-b border-border bg-background">
          <h2 className="text-lg font-semibold">Book Details</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-muted rounded-lg transition-colors text-lg"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Cover Image */}
          <div className="flex justify-center">
            <div className="w-40 h-56 rounded-lg bg-muted flex items-center justify-center text-6xl overflow-hidden">
              {book.cover_image_url ? (
                <img
                  src={book.cover_image_url}
                  alt={book.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                "📖"
              )}
            </div>
          </div>

          {/* Title */}
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-2">{book.title}</h1>
            <p className="text-sm text-muted-foreground">
              {book.authors.join(", ") || "Unknown Author"}
            </p>
          </div>

          {/* Price & Stock */}
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <div>
              <p className="text-xs text-muted-foreground">Price</p>
              <p className="text-2xl font-bold text-primary">₹{book.price.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">In Stock</p>
              <p className={`text-2xl font-bold ${book.stock > 0 ? "text-green-600" : "text-red-600"}`}>
                {book.stock}
              </p>
            </div>
          </div>

          {/* Description */}
          {book.description && (
            <div>
              <h3 className="font-semibold text-foreground mb-2">Description</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {book.description}
              </p>
            </div>
          )}

          {/* Book Details */}
          <div className="space-y-3 border-t border-border pt-4">
            {book.publisher && (
              <div>
                <p className="text-xs text-muted-foreground">Publisher</p>
                <p className="text-sm font-medium text-foreground">{book.publisher}</p>
              </div>
            )}
            {book.isbn && (
              <div>
                <p className="text-xs text-muted-foreground">ISBN</p>
                <p className="text-sm font-medium text-foreground">{book.isbn}</p>
              </div>
            )}
            {book.edition && (
              <div>
                <p className="text-xs text-muted-foreground">Edition</p>
                <p className="text-sm font-medium text-foreground">{book.edition}</p>
              </div>
            )}
            <div>
              <p className="text-xs text-muted-foreground">Language</p>
              <p className="text-sm font-medium text-foreground">{book.language}</p>
            </div>
          </div>

          {/* Categories */}
          {book.categories.length > 0 && (
            <div>
              <p className="text-xs text-muted-foreground mb-2">Categories</p>
              <div className="flex flex-wrap gap-2">
                {book.categories.map((cat) => (
                  <span
                    key={cat}
                    className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full"
                  >
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            disabled={book.stock === 0}
            className="w-full btn-primary py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {book.stock > 0 ? "Add to Cart" : "Out of Stock"}
          </button>
        </div>
      </div>
    </div>
  )
}
