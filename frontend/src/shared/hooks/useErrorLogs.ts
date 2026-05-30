import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse } from "@/shared/types"

export interface ErrorLog {
  id: string
  level: string
  endpoint: string | null
  method: string | null
  message: string
  stack_trace: string | null
  user_id: string | null
  ip_address: string | null
  status_code: number | null
  created_at: string
}

interface UseErrorLogsParams {
  page?: number
  pageSize?: number
  level?: string
  endpoint?: string
}

export function useErrorLogs(params: UseErrorLogsParams = {}) {
  const { page = 1, pageSize = 50, level, endpoint } = params
  return useQuery({
    queryKey: ["error-logs", page, pageSize, level, endpoint],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<ErrorLog>>("/error-logs", {
        params: {
          page, page_size: pageSize,
          ...(level && { level }),
          ...(endpoint && { endpoint }),
        },
      })
      return res.data
    },
  })
}