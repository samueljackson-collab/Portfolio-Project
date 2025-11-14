import React, { useRef, useState } from 'react'
import { isAxiosError } from 'axios'
import { photoService } from '../../api/services'
import type { PhotoUploadResponse } from '../../api/types'
import { LargeButton } from '../elderly/LargeButton'

type Props = {
  onUploadComplete?: (photo: PhotoUploadResponse) => void
  onUploadError?: (message: string) => void
}

export const PhotoUpload: React.FC<Props> = ({ onUploadComplete, onUploadError }) => {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [uploading, setUploading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) {
      return
    }
    setUploading(true)
    setStatusMessage('Uploading photo...')
    setErrorMessage('')
    try {
      const response = await photoService.upload(files[0])
      setStatusMessage(response.message)
      onUploadComplete?.(response)
    } catch (error) {
      let message = 'Failed to upload photo'
      if (isAxiosError(error)) {
        const detail = error.response?.data?.detail
        if (typeof detail === 'string') {
          message = detail
        }
      }
      setErrorMessage(message)
      onUploadError?.(message)
    } finally {
      setUploading(false)
    }
  }

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(event.target.files)
    event.target.value = ''
  }

  return (
    <div className="rounded-2xl border-2 border-dashed border-blue-200 bg-white p-6 text-center">
      <h2 className="text-2xl font-semibold text-blue-900">Upload a Photo</h2>
      <p className="mt-2 text-lg text-gray-600">Drag and drop a file or select one from your device.</p>
      <div className="mt-6 flex flex-col items-center gap-4">
        <LargeButton
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          className="max-w-xs"
        >
          {uploading ? 'Uploading…' : 'Choose Photo'}
        </LargeButton>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInput}
          className="sr-only"
        />
        {statusMessage && <p className="text-green-700">{statusMessage}</p>}
        {errorMessage && <p className="text-red-600">{errorMessage}</p>}
      </div>
    </div>
  )
}
