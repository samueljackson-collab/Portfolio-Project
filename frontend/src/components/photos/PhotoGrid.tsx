/**
 * PhotoGrid - Display photos in a grid with large thumbnails
 *
 * Features:
 * - Large 240x240px thumbnails
 * - Clear date and location labels
 * - Responsive grid (4-5 columns on desktop, 2-3 on tablet)
 * - Keyboard accessible
 * - Loading states
 */

import React, { useEffect, useRef, useState } from 'react'
import type { Photo } from '../../api/types'
import { photoService } from '../../api/services'
import { format, parseISO } from 'date-fns'

interface PhotoThumbnailProps {
  photoId: string
  alt: string
}

const PhotoThumbnail: React.FC<PhotoThumbnailProps> = ({ photoId, alt }) => {
  const [src, setSrc] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const objectUrlRef = useRef<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadThumbnail = async () => {
      try {
        const blob = await photoService.downloadPhotoBlob(photoId, true)
        if (cancelled) return

        if (objectUrlRef.current) {
          URL.revokeObjectURL(objectUrlRef.current)
        }

        const url = URL.createObjectURL(blob)
        objectUrlRef.current = url
        setSrc(url)
        setError(false)
      } catch (err) {
        console.error('Failed to load photo thumbnail', err)
        if (!cancelled) {
          setError(true)
        }
      }
    }

    loadThumbnail()

    return () => {
      cancelled = true
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current)
        objectUrlRef.current = null
      }
    }
  }, [photoId])

  if (error) {
    return (
      <div className="w-full h-full bg-gray-300 flex items-center justify-center text-gray-600 text-sm">
        Image unavailable
      </div>
    )
  }

  if (!src) {
    return <div className="w-full h-full bg-gray-200 animate-pulse" aria-label="Loading photo" />
  }

  return <img src={src} alt={alt} className="w-full h-full object-cover" loading="lazy" />
}

interface PhotoGridProps {
  photos: Photo[]
  onPhotoClick?: (photo: Photo) => void
  loading?: boolean
  emptyMessage?: string
}

export const PhotoGrid: React.FC<PhotoGridProps> = ({
  photos,
  onPhotoClick,
  loading = false,
  emptyMessage = 'No photos to display. Click Upload to add photos.',
}) => {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown date'
    try {
      return format(parseISO(dateString), 'MMMM d, yyyy')
    } catch {
      return 'Unknown date'
    }
  }

  const formatLocation = (photo: Photo) => {
    if (photo.city && photo.state) {
      return `${photo.city}, ${photo.state}`
    } else if (photo.city) {
      return photo.city
    } else if (photo.country) {
      return photo.country
    }
    return 'Unknown location'
  }

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-6">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-300 aspect-square rounded-lg mb-3"></div>
            <div className="h-4 bg-gray-300 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    )
  }

  if (photos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-12 text-center">
        <div className="text-6xl mb-6" role="img" aria-label="No photos">
          📷
        </div>
        <h2 className="text-2xl font-semibold text-gray-700 mb-3">No Photos Yet</h2>
        <p className="text-xl text-gray-600 max-w-md">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-6"
      role="list"
      aria-label="Photo grid"
    >
      {photos.map((photo) => (
        <button
          key={photo.id}
          onClick={() => onPhotoClick?.(photo)}
          className="
            group cursor-pointer text-left
            focus:outline-none focus:ring-4 focus:ring-blue-900 rounded-lg
            transition-transform duration-200 hover:scale-105
          "
          role="listitem"
          aria-label={`Photo from ${formatDate(photo.capture_date)}`}
        >
          {/* Photo thumbnail */}
          <div className="relative aspect-square bg-gray-200 rounded-lg overflow-hidden mb-3 shadow-md group-hover:shadow-xl transition-shadow">
            <PhotoThumbnail photoId={photo.id} alt={photo.filename} />
            <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-10 transition-opacity"></div>
          </div>

          {/* Date label */}
          <div className="text-lg font-semibold text-gray-800 mb-1 line-clamp-1">
            {formatDate(photo.capture_date || photo.upload_date)}
          </div>

          {/* Location label */}
          <div className="text-base text-gray-600 line-clamp-1">
            {formatLocation(photo)}
          </div>
        </button>
      ))}
    </div>
  )
}
