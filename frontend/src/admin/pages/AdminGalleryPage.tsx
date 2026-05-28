import { useState, useRef } from "react"
import {
  useGallery,
  useAddGalleryItem,
  useUpdateCaption,
  useDeleteGalleryItem,
} from "@/shared/hooks/useGallery"

import { LoadingSpinner } from "@/shared/components/LoadingSpinner"
import { EmptyState } from "@/shared/components/EmptyState"

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET

export function AdminGalleryPage() {
  const { data: items, isLoading } = useGallery()

  const {
    mutate: addItem,
    isPending: isUploading,
  } = useAddGalleryItem()

  const { mutate: updateCaption } = useUpdateCaption()
  const { mutate: deleteItem } = useDeleteGalleryItem()

  const [uploading, setUploading] = useState(false)
  const [uploadCaption, setUploadCaption] = useState("")
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editCaption, setEditCaption] = useState("")

  const fileInputRef = useRef<HTMLInputElement>(null)

  // Combined loading state
  const isBusy = uploading || isUploading

  const handleFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0]

    if (!file) return

    try {
      setUploading(true)

      // Upload to Cloudinary
      const formData = new FormData()
      formData.append("file", file)
      formData.append("upload_preset", UPLOAD_PRESET)
      formData.append("folder", "parkash_gallery")

      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
        {
          method: "POST",
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok || !data.secure_url) {
        throw new Error("Cloudinary upload failed")
      }

      // Save to backend
      addItem(
        {
          image_url: data.secure_url,
          public_id: data.public_id,
          caption: uploadCaption || undefined,
        },
        {
          onSuccess: () => {
            setUploadCaption("")

            if (fileInputRef.current) {
              fileInputRef.current.value = ""
            }
          },

          onError: () => {
            alert("Failed to save image.")
          },
        }
      )
    } catch (error) {
      console.error(error)
      alert("Upload failed. Please try again.")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Project Gallery
        </h2>

        <p className="text-sm text-muted-foreground mt-1">
          Upload photos visible to all customers.
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-card border border-border rounded-xl p-6 mb-6">
        <h3 className="font-semibold text-foreground mb-4">
          Upload New Photo
        </h3>

        <div className="space-y-3">
          {/* File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={isBusy}
            className="
              block w-full text-sm text-muted-foreground
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-medium
              file:bg-primary file:text-primary-foreground
              hover:file:bg-primary/90
              file:cursor-pointer
              disabled:opacity-50
            "
          />

          {/* Caption Input */}
          <input
            type="text"
            value={uploadCaption}
            onChange={(e) => setUploadCaption(e.target.value)}
            placeholder="Add a caption (optional)..."
            disabled={isBusy}
            className="
              w-full px-3 py-2.5 rounded-lg
              border border-input
              bg-background text-sm
              focus:outline-none focus:ring-2 focus:ring-ring
              disabled:opacity-50
            "
          />

          {/* Loading */}
          {isBusy && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <LoadingSpinner size="sm" />

              {uploading
                ? "Uploading image..."
                : "Saving to database..."}
            </div>
          )}
        </div>

        <p className="text-xs text-muted-foreground mt-3">
          Supports JPG, PNG, WEBP. Select a file to upload instantly.
        </p>
      </div>

      {/* Gallery */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <LoadingSpinner
            size="lg"
            text="Loading gallery..."
          />
        </div>
      ) : items?.length === 0 ? (
        <EmptyState
          title="No photos yet"
          description="Upload your first photo above."
          icon={<span className="text-4xl">🖼️</span>}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items?.map((item) => (
            <div
              key={item.id}
              className="bg-card border border-border rounded-xl overflow-hidden"
            >
              {/* Image */}
              <div className="bg-muted flex items-center justify-center overflow-hidden rounded-t-xl">
                <img src={item.image_url}
                alt={item.caption ?? "Gallery photo"}
                className="w-full h-auto object-contain max-h-72"
                loading="lazy"/>
              </div>

              {/* Content */}
              <div className="p-4 space-y-3">
                {/* Edit Mode */}
                {editingId === item.id ? (
                  <div className="flex gap-2">
                    <input
                      value={editCaption}
                      onChange={(e) =>
                        setEditCaption(e.target.value)
                      }
                      placeholder="Enter caption..."
                      autoFocus
                      className="
                        flex-1 px-2 py-1.5 rounded-lg
                        border border-input
                        bg-background text-sm
                        focus:outline-none focus:ring-2 focus:ring-ring
                      "
                    />

                    <button
                      onClick={() => {
                        updateCaption({
                          id: item.id,
                          caption: editCaption,
                        })

                        setEditingId(null)
                      }}
                      className="
                        px-3 py-1.5 rounded-lg
                        bg-primary text-primary-foreground
                        text-xs hover:bg-primary/90
                      "
                    >
                      Save
                    </button>

                    <button
                      onClick={() => setEditingId(null)}
                      className="
                        px-3 py-1.5 rounded-lg
                        border border-border
                        text-xs hover:bg-muted
                      "
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground min-h-[20px]">
                    {item.caption ? (
                      item.caption
                    ) : (
                      <span className="italic text-muted-foreground/60">
                        No caption
                      </span>
                    )}
                  </p>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {new Date(
                      item.created_at
                    ).toLocaleDateString()}
                  </span>

                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setEditingId(item.id)
                        setEditCaption(item.caption ?? "")
                      }}
                      className="text-xs text-primary hover:underline"
                    >
                      ✏️ Caption
                    </button>

                    <button
                      onClick={() => {
                        const confirmed = confirm(
                          "Delete this photo?"
                        )

                        if (confirmed) {
                          deleteItem(item.id)
                        }
                      }}
                      className="text-xs text-destructive hover:underline"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}