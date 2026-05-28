import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse, ProjectRequest, ProjectRequestStatus, Project } from "@/shared/types"

export function useAdminRequests(
  page = 1,
  pageSize = 20,
  status?: string,
  requestType?: string,
) {
  return useQuery({
    queryKey: ["admin-requests", page, pageSize, status, requestType],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<ProjectRequest>>("/project-requests", {
        params: {
          page,
          page_size: pageSize,
          ...(status && { status }),
          ...(requestType && { request_type: requestType }),
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
      const res = await api.patch(`/project-requests/${requestId}/status`, {
        status,
        admin_notes,
        rejection_reason,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-requests"] })
    },
  })
}

export function useConvertToProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (requestId: string) => {
      const res = await api.post<Project>(`/projects/from-request/${requestId}`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-requests"] })
      queryClient.invalidateQueries({ queryKey: ["admin-projects"] })
    },
  })
}