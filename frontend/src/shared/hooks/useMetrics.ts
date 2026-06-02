import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"

export interface MetricsSummary {
  today_new_users: number
  today_logins: number
  today_failed_logins: number
  today_requests: number
  today_reviews: number
  today_errors: number
  week_new_users: number
  week_logins: number
  week_requests: number
  week_reviews: number
  week_errors: number
  total_users: number
  total_books: number
  total_requests: number
  total_projects: number
  total_reviews: number
}

export interface MetricsHourly {
  hour: string
  new_users: number
  logins_success: number
  logins_failed: number
  requests_submitted: number
  projects_created: number
  reviews_submitted: number
  books_added: number
  errors_count: number
}

export function useMetricsSummary() {
  return useQuery({
    queryKey: ["metrics", "summary"],
    queryFn: async () => {
      const res = await api.get<MetricsSummary>("/metrics/summary")
      return res.data
    },
    refetchInterval: 60000, // refresh every minute
  })
}

export function useMetricsTrend() {
  return useQuery({
    queryKey: ["metrics", "trend"],
    queryFn: async () => {
      const res = await api.get<{ data: MetricsHourly[] }>("/metrics/trend")
      return res.data.data
    },
  })
}