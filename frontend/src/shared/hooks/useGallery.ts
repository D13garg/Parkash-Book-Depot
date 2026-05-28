import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/axios"
import type { GalleryItem } from "@/shared/types"

export function useGallery() {
  return useQuery({
    queryKey: ["gallery"],
    queryFn: async () => {
      const res = await api.get<GalleryItem[]>("/gallery")
      return res.data
    },
  })
}

export function useAddGalleryItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: {
      image_url: string
      public_id: string
      caption?: string
    }) => {
      const res = await api.post<GalleryItem>("/gallery", data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gallery"] })
    },
  })
}

export function useUpdateCaption() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, caption }: { id: string; caption: string }) => {
      const res = await api.patch<GalleryItem>(`/gallery/${id}/caption`, { caption })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gallery"] })
    },
  })
}

export function useDeleteGalleryItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/gallery/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gallery"] })
    },
  })
}