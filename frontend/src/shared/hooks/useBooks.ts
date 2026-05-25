import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse, Book } from "@/shared/types"

interface UseBooksParams {
  page?: number
  pageSize?: number
  category?: string
  search?: string
  inStockOnly?: boolean
  minPrice?: number
  maxPrice?: number
}

export function useBooks(params: UseBooksParams = {}) {
  const {
    page = 1,
    pageSize = 20,
    category,
    search,
    inStockOnly,
    minPrice,
    maxPrice,
  } = params

  return useQuery({
    queryKey: ["books", page, pageSize, category, search, inStockOnly, minPrice, maxPrice],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Book>>("/books", {
        params: {
          page,
          page_size: pageSize,
          ...(category && { category }),
          ...(search && { search }),
          ...(inStockOnly && { in_stock_only: true }),
          ...(minPrice !== undefined && { min_price: minPrice }),
          ...(maxPrice !== undefined && { max_price: maxPrice }),
        },
      })
      return res.data
    },
  })
}

export function useBook(bookId: string) {
  return useQuery({
    queryKey: ["books", bookId],
    queryFn: async () => {
      const res = await api.get<Book>(`/books/${bookId}`)
      return res.data
    },
    enabled: !!bookId,
  })
}
