import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse, ProjectRequest, ProjectRequestStatus } from "@/shared/types"

export function useAdminRequests(page = 1, pageSize = 20, status?: string) {
  return useQuery({
    queryKey: ["project-requests", "admin", page, pageSize, status],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<ProjectRequest>>("/project-requests", {
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

export function useUpdateRequestStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      requestId,
      status,
      admin_notes,
      rejection_reason,
    }: {
      requestId: string
      status: ProjectRequestStatus
      admin_notes?: string
      rejection_reason?: string
    }) => {
      const res = await api.patch<ProjectRequest>(
        `/project-requests/${requestId}/status`,
        { status, admin_notes, rejection_reason }
      )
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-requests"] })
    },
  })
}
