import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate, useParams } from "react-router-dom"
import { useBook, useUpdateBook } from "@/shared/hooks/useAdminBooks"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

const schema = z.object({
  title:               z.string().min(1, "Title is required"),
  authors:             z.string().min(1, "At least one author required"),
  categories:          z.string().min(1, "At least one category required"),
  price:               z.coerce.number().positive("Price must be greater than 0"),
  stock:               z.coerce.number().int().min(0, "Stock cannot be negative"),
  publisher:           z.string().optional(),
  isbn:                z.string().optional(),
  description:         z.string().optional(),
  language:            z.string().optional(),
  low_stock_threshold: z.coerce.number().int().min(0).optional(),
})

type FormData = z.infer<typeof schema>

export function EditBookPage() {
  const { bookId = "" } = useParams()
  const navigate = useNavigate()
  const { data: book, isLoading, isError } = useBook(bookId)
  const { mutate: updateBook, isPending, error, isSuccess } = useUpdateBook(bookId)

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    resolver: zodResolver(schema),
  })

  useEffect(() => {
    if (!book) return
    reset({
      title: book.title,
      authors: book.authors.join(", "),
      categories: book.categories.join(", "),
      price: book.price,
      stock: book.stock,
      publisher: book.publisher ?? "",
      isbn: book.isbn ?? "",
      description: book.description ?? "",
      language: book.language || "English",
      low_stock_threshold: book.low_stock_threshold ?? 5,
    })
  }, [book, reset])

  const onSubmit = (data: FormData) => {
    updateBook(
      {
        title: data.title,
        authors: data.authors.split(",").map((a) => a.trim()).filter(Boolean),
        categories: data.categories.split(",").map((c) => c.trim()).filter(Boolean),
        price: data.price,
        stock: data.stock,
        publisher: data.publisher || undefined,
        isbn: data.isbn || undefined,
        description: data.description || undefined,
        language: data.language || "English",
        low_stock_threshold: data.low_stock_threshold ?? 5,
      },
      {
        onSuccess: () => {
          setTimeout(() => navigate("/admin/books"), 1200)
        },
      }
    )
  }

  const errorMessage = error
    ? (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to update book."
    : null

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading book..." />
      </div>
    )
  }

  if (isError || !book) {
    return (
      <EmptyState
        title="Book not found"
        description="This book may have been removed or the link is invalid."
        icon={<span className="text-4xl">📚</span>}
        action={
          <button onClick={() => navigate("/admin/books")} className="btn-primary">
            Back to books
          </button>
        }
      />
    )
  }

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => navigate("/admin/books")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 mb-6 transition-colors"
      >
        ← Back to books
      </button>

      <div className="page-header mb-6">
        <h2>Edit Book</h2>
        <p>Update details for &ldquo;{book.title}&rdquo;</p>
      </div>

      <div className="surface-card p-6">
        {isSuccess && (
          <div className="mb-4 alert-success">
            Book updated successfully! Redirecting...
          </div>
        )}
        {errorMessage && (
          <div className="mb-4 alert-error">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Title <span className="text-destructive">*</span></label>
            <input {...register("title")} className="input-field" />
            {errors.title && <p className="mt-1 text-xs text-destructive">{errors.title.message}</p>}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Authors <span className="text-destructive">*</span>
                <span className="text-muted-foreground font-normal"> (comma separated)</span>
              </label>
              <input {...register("authors")} placeholder="Author 1, Author 2" className="input-field" />
              {errors.authors && <p className="mt-1 text-xs text-destructive">{errors.authors.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Categories <span className="text-destructive">*</span>
                <span className="text-muted-foreground font-normal"> (comma separated)</span>
              </label>
              <input {...register("categories")} placeholder="textbook, science" className="input-field" />
              {errors.categories && <p className="mt-1 text-xs text-destructive">{errors.categories.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Price (₹) <span className="text-destructive">*</span></label>
              <input {...register("price")} type="number" step="0.01" min="0" className="input-field" />
              {errors.price && <p className="mt-1 text-xs text-destructive">{errors.price.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Stock</label>
              <input {...register("stock")} type="number" min="0" className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Low Stock Alert</label>
              <input {...register("low_stock_threshold")} type="number" min="0" className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Language</label>
              <input {...register("language")} className="input-field" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Publisher</label>
              <input {...register("publisher")} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">ISBN</label>
              <input {...register("isbn")} className="input-field" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Description</label>
            <textarea {...register("description")} rows={3} className="input-field resize-none" />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={isPending} className="flex-1 btn-primary">
              {isPending ? "Saving..." : "Save Changes"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/admin/books")}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
