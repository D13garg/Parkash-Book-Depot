import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse, ProjectRequest } from "@/shared/types"

interface SubmitRequestData {
  title: string
  description: string
  category: string
  requirements?: string
  quantity?: number
  institution_name?: string
  institution_address?: string
  contact_phone?: string
}

export function useProjectRequests(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["project-requests", page, pageSize],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<ProjectRequest>>("/project-requests", {
        params: { page, page_size: pageSize },
      })
      return res.data
    },
  })
}

export function useSubmitProjectRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: SubmitRequestData) => {
      const res = await api.post<ProjectRequest>("/project-requests", data)
      return res.data
    },
    onSuccess: () => {
      // Invalidate so the requests list refreshes automatically
      queryClient.invalidateQueries({ queryKey: ["project-requests"] })
    },
  })
}
