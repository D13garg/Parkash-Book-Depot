import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { PaginatedResponse, Project, ProjectUpdate, ProjectStatus } from "@/shared/types"

interface AddUpdateData {
  message: string
  status_changed_to?: ProjectStatus
  attachments?: string[]
}

export function useProjects(page = 1, pageSize = 20, status?: string) {
  return useQuery({
    queryKey: ["projects", page, pageSize, status],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Project>>("/projects", {
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

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: async () => {
      const res = await api.get<Project>(`/projects/${projectId}`)
      return res.data
    },
    enabled: !!projectId,
  })
}

export function useProjectUpdates(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId, "updates"],
    queryFn: async () => {
      const res = await api.get<ProjectUpdate[]>(`/projects/${projectId}/updates`)
      return res.data
    },
    enabled: !!projectId,
  })
}

export function useAddProjectUpdate(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: AddUpdateData) => {
      const res = await api.post<ProjectUpdate>(
        `/projects/${projectId}/updates`,
        data
      )
      return res.data
    },
    onSuccess: () => {
      // Refresh both the project (status may have changed) and the timeline
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "updates"] })
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
  })
}
