import React, { useEffect, useState } from 'react'
import type { Photo } from '../../api/types'
import { photoService } from '../../api/services'
import { SidebarNav } from '../../components/elderly/SidebarNav'
import { PhotoGrid } from '../../components/photos/PhotoGrid'
import { PhotoUpload } from '../../components/photos/PhotoUpload'
import { PhotoCalendar } from '../../components/photos/PhotoCalendar'

type ViewMode = 'grid' | 'calendar' | 'upload'

const NAV_ITEMS = [
  { id: 'grid', label: 'All Photos' },
  { id: 'calendar', label: 'Calendar View' },
  { id: 'upload', label: 'Upload Photo' },
]

export const PhotosPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [photos, setPhotos] = useState<Photo[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [selectedDatePhotos, setSelectedDatePhotos] = useState<Photo[]>([])

  const loadPhotos = async () => {
    setLoading(true)
    try {
      const response = await photoService.list()
      setPhotos(response.items)
    } catch (error) {
      setMessage('Unable to load photos right now. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPhotos()
  }, [])

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 md:flex-row">
      <aside className="w-full md:w-64">
        <SidebarNav items={NAV_ITEMS} activeId={viewMode} onSelect={(id) => setViewMode(id as ViewMode)} />
      </aside>
      <main className="flex-1 space-y-6">
        <header>
          <h1 className="text-3xl font-bold text-blue-900">ElderPhoto</h1>
          <p className="text-gray-600">Upload, browse, and revisit treasured memories.</p>
        </header>
        {message && (
          <div className="rounded-xl bg-blue-50 p-4 text-blue-900" role="status">
            {message}
          </div>
        )}
        {viewMode === 'grid' && <PhotoGrid photos={photos} loading={loading} />}
        {viewMode === 'calendar' && (
          <div className="space-y-4">
            <PhotoCalendar onDateSelect={(date, list) => setSelectedDatePhotos(list)} />
            {selectedDatePhotos.length > 0 && (
              <div className="rounded-xl border border-blue-100 p-4">
                <p className="font-semibold text-blue-900">Photos on selected date</p>
                <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                  {selectedDatePhotos.map((photo) => (
                    <div key={photo.id} className="rounded-lg bg-white p-3 shadow">
                      <p className="text-gray-800">{photo.location_name || photo.file_name}</p>
                      <p className="text-sm text-gray-500">{photo.capture_date}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {viewMode === 'upload' && (
          <PhotoUpload
            onUploadComplete={(photo) => {
              setMessage(photo.message)
              setViewMode('grid')
              loadPhotos()
            }}
            onUploadError={(error) => setMessage(error)}
          />
        )}
      </main>
    </div>
  )
}
