/**
 * PhotosPage - Main elderly-friendly photo management page
 *
 * Features:
 * - Windows XP-style sidebar navigation
 * - Photo grid with large thumbnails
 * - Calendar view
 * - Upload interface
 * - Location-based organization
 */

import React, { useState, useEffect } from 'react'
import { photoService, albumService } from '../../api/services'
import type { Photo, Album, PhotoUploadResponse } from '../../api/types'
import { SidebarNav, type NavItem } from '../../components/elderly/SidebarNav'
import { LargeButton } from '../../components/elderly/LargeButton'
import { PhotoGrid } from '../../components/photos/PhotoGrid'
import { PhotoUpload } from '../../components/photos/PhotoUpload'
import { PhotoCalendar } from '../../components/photos/PhotoCalendar'

type ViewMode = 'all' | 'calendar' | 'upload' | 'album' | 'location'

export const PhotosPage: React.FC = () => {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [albums, setAlbums] = useState<Album[]>([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('all')
  const [selectedAlbumId, setSelectedAlbumId] = useState<string | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    loadPhotos()
    loadAlbums()
  }, [])

  const loadPhotos = async (filters?: { album_id?: string }) => {
    setLoading(true)
    try {
      const response = await photoService.getAll({ page_size: 100, ...filters })
      setPhotos(response.items)
    } catch (error) {
      console.error('Failed to load photos:', error)
      setErrorMessage('Failed to load photos. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const loadAlbums = async () => {
    try {
      const response = await albumService.getAll({ page_size: 100 })
      setAlbums(response.items)
    } catch (error) {
      console.error('Failed to load albums:', error)
    }
  }

  const handleUploadComplete = (response: PhotoUploadResponse) => {
    setSuccessMessage(
      `Photo uploaded successfully${response.album ? ` to ${response.album.name}` : ''}!`
    )
    loadPhotos()
    loadAlbums()
    setShowUploadModal(false)

    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(''), 5000)
  }

  const handleUploadError = (error: string) => {
    setErrorMessage(error)
    setTimeout(() => setErrorMessage(''), 5000)
  }

  const handleViewAllPhotos = () => {
    setViewMode('all')
    setSelectedAlbumId(null)
    loadPhotos()
  }

  const handleViewAlbum = (albumId: string) => {
    setViewMode('album')
    setSelectedAlbumId(albumId)
    loadPhotos({ album_id: albumId })
  }

  const handleViewCalendar = () => {
    setViewMode('calendar')
  }

  const handleViewUpload = () => {
    setViewMode('upload')
  }

  // Build navigation items
  const locationAlbums = albums.filter((a) => a.type === 'location')

  const navItems: NavItem[] = [
    {
      id: 'all-photos',
      label: 'All Photos',
      icon: '📷',
      count: photos.length,
      onClick: handleViewAllPhotos,
    },
    {
      id: 'by-location',
      label: 'By Location',
      icon: '📍',
      children: locationAlbums.map((album) => ({
        id: album.id,
        label: album.name,
        icon: '📁',
        count: album.photo_count,
        onClick: () => handleViewAlbum(album.id),
      })),
    },
    {
      id: 'calendar',
      label: 'Calendar',
      icon: '📅',
      onClick: handleViewCalendar,
    },
    {
      id: 'upload',
      label: 'Upload Photos',
      icon: '⬆️',
      onClick: handleViewUpload,
    },
  ]

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar Navigation */}
      <aside className="w-80 bg-white shadow-lg">
        <div className="p-6 border-b-2 border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <span role="img" aria-label="Photos">
              📷
            </span>
            My Photos
          </h1>
        </div>
        <SidebarNav items={navItems} activeId={selectedAlbumId || viewMode} />
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white border-b-2 border-gray-200 px-8 py-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800">
              {viewMode === 'all' && 'All Photos'}
              {viewMode === 'calendar' && 'Calendar View'}
              {viewMode === 'upload' && 'Upload Photos'}
              {viewMode === 'album' &&
                albums.find((a) => a.id === selectedAlbumId)?.name}
            </h2>
            <p className="text-lg text-gray-600 mt-1">
              {viewMode === 'all' && `${photos.length} photos`}
              {viewMode === 'calendar' && 'Find photos by date'}
              {viewMode === 'upload' && 'Add new photos to your collection'}
              {viewMode === 'album' && `${photos.length} photos in this album`}
            </p>
          </div>

          {viewMode !== 'upload' && (
            <LargeButton
              variant="primary"
              size="large"
              icon="⬆️"
              onClick={handleViewUpload}
            >
              Upload Photos
            </LargeButton>
          )}
        </header>

        {/* Messages */}
        {successMessage && (
          <div className="mx-8 mt-6 p-4 bg-green-100 border-2 border-green-600 rounded-lg">
            <p className="text-lg text-green-800 font-semibold">{successMessage}</p>
          </div>
        )}

        {errorMessage && (
          <div className="mx-8 mt-6 p-4 bg-red-100 border-2 border-red-600 rounded-lg">
            <p className="text-lg text-red-800 font-semibold">{errorMessage}</p>
          </div>
        )}

        {/* Content Area */}
        <div className="p-8">
          {viewMode === 'upload' && (
            <PhotoUpload
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
            />
          )}

          {viewMode === 'calendar' && (
            <PhotoCalendar
              onDateSelect={(date, photos) => {
                console.log('Selected date:', date, 'Photos:', photos)
                // Could show photos from that date
              }}
            />
          )}

          {(viewMode === 'all' || viewMode === 'album') && (
            <PhotoGrid
              photos={photos}
              loading={loading}
              onPhotoClick={(photo) => {
                console.log('Photo clicked:', photo)
                // Could open photo detail modal
              }}
            />
          )}
        </div>
      </main>
    </div>
  )
}
