import { useState } from "react"
import { useBooks } from "@/shared/hooks/useBooks"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

export function BooksPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [category, setCategory] = useState("")
  const [inStockOnly, setInStockOnly] = useState(false)

  const { data, isLoading, isError } = useBooks({
    page,
    search,
    category,
    inStockOnly,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  const handleCategoryChange = (val: string) => {
    setCategory(val)
    setPage(1)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading books..." />
      </div>
    )
  }

  if (isError) {
    return (
      <EmptyState
        title="Failed to load books"
        description="Something went wrong. Please try again."
        icon={<span className="text-4xl">⚠️</span>}
      />
    )
  }

  return (
    <div>
      <div className="page-header mb-6">
        <h2>Browse Books</h2>
        <p>{data?.total ?? 0} books available</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <form onSubmit={handleSearch} className="flex gap-2 flex-1">
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by title or author..."
            className="input-field flex-1"
          />
          <button
            type="submit"
            className="btn-primary"
          >
            Search
          </button>
        </form>

        <select
          value={category}
          onChange={(e) => handleCategoryChange(e.target.value)}
          className="input-field"
        >
          <option value="">All categories</option>
          <option value="textbook">Textbooks</option>
          <option value="fiction">Fiction</option>
          <option value="non-fiction">Non-Fiction</option>
          <option value="reference">Reference</option>
          <option value="children">Children</option>
        </select>

        <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => { setInStockOnly(e.target.checked); setPage(1) }}
            className="rounded"
          />
          In stock only
        </label>
      </div>

      {/* Books grid */}
      {data?.items.length === 0 ? (
        <EmptyState
          title="No books found"
          description="Try adjusting your search or filters."
          icon={<span className="text-4xl">📚</span>}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data?.items.map((book) => (
              <div
                key={book.id}
                className="surface-card surface-card-interactive p-4 flex flex-col gap-3"
              >
                {/* Cover placeholder */}
                <div className="aspect-[3/4] bg-muted rounded-lg flex items-center justify-center text-4xl">
                  {book.cover_image_url
                    ? <img src={book.cover_image_url} alt={book.title} className="w-full h-full object-cover rounded-lg" />
                    : "📖"
                  }
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-foreground text-sm leading-snug line-clamp-2">
                    {book.title}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {book.authors.join(", ") || "Unknown Author"}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-base font-bold text-primary">
                    {book.price ? `₹${book.price.toFixed(2)}` : "Price unavailable"}
                  </span>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    (book.stock ?? 0) > 0 ? "badge-success": "badge-neutral"}`}>
                      {book.stock != null ? `${book.stock} in stock` : "Stock unknown"}
                      </span>
                </div>

                {book.categories?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {book.categories.slice(0, 2).map((cat) => (
                      <span
                        key={cat}
                        className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                )}
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
