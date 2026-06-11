import { useQuery } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { User } from "@/shared/types"

async function fetchAssociates(): Promise<User[]> {
  const res = await api.get<User[]>("/users/associates")
  return res.data
}

export function useAssociates() {
  return useQuery({
    queryKey: ["associates"],
    queryFn: fetchAssociates,
    staleTime: 5 * 60 * 1000, // 5 minutes — associates list changes rarely
  })
}