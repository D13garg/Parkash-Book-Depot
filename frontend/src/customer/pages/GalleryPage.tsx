import { useGallery } from "@/shared/hooks/useGallery"
import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

export function GalleryPage() {
  const { data: items, isLoading, isError } = useGallery()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <LoadingSpinner size="lg" text="Loading gallery..." />
      </div>
    )
  }

  if (isError) {
    return <EmptyState title="Failed to load gallery" icon={<span className="text-4xl">⚠️</span>} />
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Project Gallery</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Photos from our completed projects and store.
        </p>
      </div>

      {items?.length === 0 ? (
        <EmptyState
          title="No photos yet"
          description="Check back soon for photos from our projects."
          icon={<span className="text-4xl">🖼️</span>}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items?.map((item) => (
            <div
              key={item.id}
              className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="bg-muted flex items-center justify-center overflow-hidden rounded-t-xl">
                 <img src={item.image_url}
                 alt={item.caption ?? "Gallery photo"}
                 className="w-full h-auto object-contain max-h-72"
                 loading="lazy"/>
                 </div>

              {item.caption && (
                <div className="px-4 py-3">
                  <p className="text-sm text-foreground">{item.caption}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}