import { useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { Project, ProjectStatus, ProjectUpdate } from "@/shared/types"
import {
  useProjects,
  useProject,
  useProjectUpdates,
} from "@/shared/hooks/useProjects"

export function useAdminProjects(page = 1, pageSize = 20, status?: string) {
  return useProjects(page, pageSize, status)
}

export function useAdminProject(projectId: string) {
  return useProject(projectId)
}

export function useAdminProjectUpdates(projectId: string) {
  return useProjectUpdates(projectId)
}

export function useAssignAssociate(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (associateId: string) => {
      const res = await api.patch<Project>(`/projects/${projectId}/assign`, {
        associate_id: associateId,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
  })
}

export function useUpdateProjectStatus(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: { status: ProjectStatus; notes?: string }) => {
      const res = await api.patch<Project>(`/projects/${projectId}/status`, data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "updates"] })
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
  })
}

export function useConvertRequestToProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (requestId: string) => {
      const res = await api.post<Project>(`/projects/from-request/${requestId}`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-requests"] })
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
  })
}

export type { ProjectUpdate }
