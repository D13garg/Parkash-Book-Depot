import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate } from "react-router-dom"
import { useCreateBook } from "@/shared/hooks/useAdminBooks"

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

export function AddBookPage() {
  const navigate = useNavigate()
  const { mutate: createBook, isPending, error, isSuccess } = useCreateBook()

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { language: "English", stock: 0, low_stock_threshold: 5 },
  })

  const onSubmit = (data: FormData) => {
    createBook(
      {
        ...data,
        authors:    data.authors.split(",").map((a) => a.trim()).filter(Boolean),
        categories: data.categories.split(",").map((c) => c.trim()).filter(Boolean),
        language:   data.language || "English",
        low_stock_threshold: data.low_stock_threshold ?? 5,
      },
      {
        onSuccess: () => {
          reset()
          setTimeout(() => navigate("/admin/books"), 1200)
        },
      }
    )
  }

  const errorMessage = error
    ? (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to create book."
    : null

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => navigate("/admin/books")}
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 mb-6 transition-colors"
      >
        ← Back to books
      </button>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Add New Book</h2>
        <p className="text-sm text-muted-foreground mt-1">Fill in the book details below.</p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6">
        {isSuccess && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 text-green-700 text-sm">
            Book added successfully! Redirecting...
          </div>
        )}
        {errorMessage && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Title <span className="text-destructive">*</span></label>
            <input {...register("title")} className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            {errors.title && <p className="mt-1 text-xs text-destructive">{errors.title.message}</p>}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Authors <span className="text-destructive">*</span>
                <span className="text-muted-foreground font-normal"> (comma separated)</span>
              </label>
              <input {...register("authors")} placeholder="Author 1, Author 2" className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.authors && <p className="mt-1 text-xs text-destructive">{errors.authors.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Categories <span className="text-destructive">*</span>
                <span className="text-muted-foreground font-normal"> (comma separated)</span>
              </label>
              <input {...register("categories")} placeholder="textbook, science" className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.categories && <p className="mt-1 text-xs text-destructive">{errors.categories.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Price (₹) <span className="text-destructive">*</span></label>
              <input {...register("price")} type="number" step="0.01" min="0" className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.price && <p className="mt-1 text-xs text-destructive">{errors.price.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Stock</label>
              <input {...register("stock")} type="number" min="0" className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Low Stock Alert</label>
              <input {...register("low_stock_threshold")} type="number" min="0" className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Language</label>
              <input {...register("language")} className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Publisher</label>
              <input {...register("publisher")} className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">ISBN</label>
              <input {...register("isbn")} className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Description</label>
            <textarea {...register("description")} rows={3} className="w-full px-3 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none" />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 py-2.5 px-4 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              {isPending ? "Adding..." : "Add Book"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/admin/books")}
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
