import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"

export interface AnalyticsData {
  summary: {
    total_requests: number
    total_projects: number
    completed_projects: number
    completion_rate_percent: number
    total_reviews: number
    low_stock_count: number
    error_count_24h: number
  }
  request_conversion_rate: number
  associate_performance: {
    associate_id: string
    associate_name: string
    associate_email: string
    assigned_projects: number
    completed_projects: number
    open_projects: number
    avg_completion_days: number | null
  }[]
  review_metrics: {
    average_rating: number
    total_reviews: number
    reviews_this_month: number
  }
  low_stock_books: {
    id: string
    title: string
    stock: number
    low_stock_threshold: number
  }[]
  stale_requests: {
    id: string
    title: string
    category: string
    status: string
    days_old: number
    customer_id: string
  }[]
  inactive_projects: {
    id: string
    title: string
    status: string
    assigned_to: string | null
    days_since_update: number
  }[]
}

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: async () => {
      const res = await api.get<AnalyticsData>("/analytics")
      return res.data
    },
    staleTime: 1000 * 60 * 5, // 5 min cache
  })
}