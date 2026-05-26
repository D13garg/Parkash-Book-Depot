import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { Review } from "@/shared/types"

interface SubmitReviewData {
  rating: number
  category: string
  message: string
}

export function useMyReviews() {
  return useQuery({
    queryKey: ["reviews", "mine"],
    queryFn: async () => {
      const res = await api.get<Review[]>("/reviews/mine")
      return res.data
    },
  })
}

export function useSubmitReview() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: SubmitReviewData) => {
      const res = await api.post<Review>("/reviews", data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "mine"] })
    },
  })
}

export function useAllReviews() {
  return useQuery({
    queryKey: ["reviews", "all"],
    queryFn: async () => {
      const res = await api.get<Review[]>("/reviews")
      return res.data
    },
  })
}