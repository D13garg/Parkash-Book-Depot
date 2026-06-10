import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse } from "@/shared/types"

export interface OrderItem {
  book_id: string
  title: string
  price: number
  quantity: number
  subtotal: number
}

export interface Order {
  id: string
  customer_id: string
  customer_name: string
  items: OrderItem[]
  total_amount: number
  status: string
  delivery_address: string
  phone: string
  notes: string | null
  created_at: string
  updated_at: string
}

export interface PlaceOrderData {
  items: { book_id: string; quantity: number }[]
  delivery_address: string
  phone: string
  notes?: string
}

export function useMyOrders(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["orders", "mine", page, pageSize],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Order>>("/orders/mine", {
        params: { page, page_size: pageSize },
      })
      return res.data
    },
  })
}

export function usePlaceOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: PlaceOrderData) => {
      const res = await api.post<Order>("/orders", data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
      queryClient.invalidateQueries({ queryKey: ["books"] })
    },
  })
}

export function useAdminOrders(
  page = 1,
  pageSize = 20,
  status?: string,
) {
  return useQuery({
    queryKey: ["admin-orders", page, pageSize, status],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Order>>("/orders", {
        params: {
          page,
          page_size: pageSize,
          ...(status && { status }),
        },
      })
      return res.data
    },
  })
}

export function useUpdateOrderStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      orderId,
      status,
    }: {
      orderId: string
      status: string
    }) => {
      const res = await api.patch<Order>(
        `/orders/${orderId}/status`,
        { status },
      )
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["admin-orders"],
      })
    },
  })
}