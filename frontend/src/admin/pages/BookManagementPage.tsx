import { useState } from "react"
import { Link } from "react-router-dom"
import { useAdminBooks, useLowStockBooks } from "@/shared/hooks/useAdminBooks"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"
import { Pagination } from "@/shared/components/Pagination"

export function BookManagementPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")

  const { data, isLoading, isError } = useAdminBooks(page, 20, search || undefined)
  const { data: lowStock } = useLowStockBooks()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
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
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Book Management</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {data?.total ?? 0} books in catalog
          </p>
        </div>
        <Link
          to="/admin/books/add"
          className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
        >
          + Add Book
        </Link>
      </div>

      {lowStock && lowStock.length > 0 && (
        <div className="mb-6 px-4 py-3 rounded-xl bg-orange-50 border border-orange-200 text-sm text-orange-800">
          <span className="font-medium">{lowStock.length} book{lowStock.length > 1 ? "s" : ""}</span> below low-stock threshold
        </div>
      )}

      <form onSubmit={handleSearch} className="flex gap-2 mb-6 max-w-md">
        <input
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search by title or author..."
          className="flex-1 px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-primary text-primary-foreground text-sm rounded-lg hover:bg-primary/90 transition-colors"
        >
          Search
        </button>
      </form>

      {!data || data.items.length === 0 ? (
        <EmptyState
          title="No books found"
          description="Add your first book to the catalog."
          icon={<span className="text-4xl">📚</span>}
          action={
            <Link
              to="/admin/books/add"
              className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
            >
              Add Book
            </Link>
          }
        />
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Title</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground hidden sm:table-cell">Authors</th>
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground">Price</th>
                  <th className="text-right px-4 py-3 font-medium text-muted-foreground">Stock</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground hidden md:table-cell">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data!.items.map((book) => (
                  <tr key={book.id} className="bg-card hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-medium text-foreground">{book.title}</td>
                    <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">
                      {book.authors.join(", ")}
                    </td>
                    <td className="px-4 py-3 text-right">₹{book.price.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right">
                      <span className={book.is_low_stock ? "text-orange-600 font-medium" : ""}>
                        {book.stock}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      {!book.is_active ? (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">Inactive</span>
                      ) : book.is_low_stock ? (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700">Low stock</span>
                      ) : (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Active</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
