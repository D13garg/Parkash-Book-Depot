import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { AuditLog, PaginatedResponse } from "@/shared/types"

interface UseAuditLogsParams {
  page?: number
  pageSize?: number
  action?: string
  entityType?: string
}

export function useAuditLogs(params: UseAuditLogsParams = {}) {
  const { page = 1, pageSize = 50, action, entityType } = params
  return useQuery({
    queryKey: ["audit-logs", page, pageSize, action, entityType],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<AuditLog>>("/audit-logs", {
        params: {
          page, page_size: pageSize,
          ...(action && { action }),
          ...(entityType && { entity_type: entityType }),
        },
      })
      return res.data
    },
  })
}

export function useEntityAuditLogs(entityType: string, entityId: string) {
  return useQuery({
    queryKey: ["audit-logs", entityType, entityId],
    queryFn: async () => {
      const res = await api.get<AuditLog[]>(`/audit-logs/entity/${entityType}/${entityId}`)
      return res.data
    },
    enabled: !!entityType && !!entityId,
  })
}