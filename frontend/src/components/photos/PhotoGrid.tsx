import React, { useEffect, useState } from 'react'
import type { Photo } from '../../api/types'
import { photoService } from '../../api/services'

type Props = {
  photos: Photo[]
  loading?: boolean
}

const PhotoThumbnail: React.FC<{ photo: Photo }> = ({ photo }) => {
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    let url: string | null = null
    const load = async () => {
      try {
        const blob = await photoService.fetchPhotoBlob(photo.id, { thumbnail: true })
        if (!cancelled) {
          url = URL.createObjectURL(blob)
          setSrc(url)
        }
      } catch (error) {
        console.error('Failed to load photo thumbnail', error)
      }
    }
    load()
    return () => {
      cancelled = true
      if (url) {
        URL.revokeObjectURL(url)
      }
    }
  }, [photo.id])

  return (
    <figure className="rounded-xl bg-white p-2 shadow-sm" aria-label={photo.title ?? 'Uploaded photo'}>
      {src ? (
        <img
          src={src}
          alt={photo.title ?? 'Photo'}
          className="h-48 w-full rounded-lg object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-48 w-full items-center justify-center rounded-lg bg-blue-50 text-blue-700">
          Loading…
        </div>
      )}
      <figcaption className="mt-2 text-center text-sm text-gray-700">
        {photo.location_name || photo.capture_date || photo.file_name}
      </figcaption>
    </figure>
  )
}

export const PhotoGrid: React.FC<Props> = ({ photos, loading = false }) => {
  if (loading) {
    return <p className="text-center text-lg text-gray-600">Loading photos…</p>
  }

  if (photos.length === 0) {
    return <p className="text-center text-lg text-gray-600">No photos yet. Upload one to get started!</p>
  }

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {photos.map((photo) => (
        <PhotoThumbnail key={photo.id} photo={photo} />
      ))}
    </div>
  )
}
