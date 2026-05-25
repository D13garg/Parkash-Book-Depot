import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { Book, PaginatedResponse } from "@/shared/types"

export interface CreateBookData {
  title: string
  authors: string[]
  categories: string[]
  price: number
  stock: number
  publisher?: string
  isbn?: string
  description?: string
  language?: string
  low_stock_threshold?: number
}

export function useAdminBooks(page = 1, pageSize = 20, search?: string) {
  return useQuery({
    queryKey: ["admin-books", page, pageSize, search],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Book>>("/books", {
        params: {
          page,
          page_size: pageSize,
          ...(search && { search }),
        },
      })
      return res.data
    },
  })
}

export function useLowStockBooks() {
  return useQuery({
    queryKey: ["admin-books", "low-stock"],
    queryFn: async () => {
      const res = await api.get<Book[]>("/books/admin/low-stock")
      return res.data
    },
  })
}

export function useCreateBook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateBookData) => {
      const res = await api.post<Book>("/books", data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-books"] })
      queryClient.invalidateQueries({ queryKey: ["books"] })
    },
  })
}

export function useUpdateStock(bookId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (stock: number) => {
      const res = await api.patch<Book>(`/books/${bookId}/stock`, { stock })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-books"] })
      queryClient.invalidateQueries({ queryKey: ["books"] })
    },
  })
}

export function useDeleteBook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (bookId: string) => {
      await api.delete(`/books/${bookId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-books"] })
      queryClient.invalidateQueries({ queryKey: ["books"] })
    },
  })
}
