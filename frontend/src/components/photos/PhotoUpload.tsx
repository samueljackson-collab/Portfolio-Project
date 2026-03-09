/**
 * PhotoUpload - Upload interface with drag-and-drop
 *
 * Features:
 * - Drag and drop support
 * - Large upload button
 * - Clear instructions
 * - Multiple file support
 * - Upload progress indication
 * - Error handling
 */

import React, { useState, useRef } from 'react'
import { AxiosError } from 'axios'
import { photoService } from '../../api/services'
import type { PhotoUploadResponse, ApiError } from '../../api/types'
import { LargeButton } from '../elderly/LargeButton'

interface PhotoUploadProps {
  onUploadComplete?: (response: PhotoUploadResponse) => void
  onUploadError?: (error: string) => void
}

export const PhotoUpload: React.FC<PhotoUploadProps> = ({
  onUploadComplete,
  onUploadError,
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadingFile, setUploadingFile] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const MAX_FILE_SIZE_MB = 20

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    // Process files one at a time
    for (let i = 0; i < files.length; i++) {
      const file = files[i]

      // Validate file type
      if (!file.type.startsWith('image/')) {
        onUploadError?.(`${file.name} is not an image file`)
        continue
      }

      // Validate file size (20MB max)
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        onUploadError?.(
          `${file.name} is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`
        )
        continue
      }

      try {
        setUploading(true)
        setUploadingFile(file.name)

        const response = await photoService.upload(file)
        onUploadComplete?.(response)
      } catch (error) {
        const axiosError = error as AxiosError<ApiError>
        let errorMessage = 'Failed to upload photo'

        if (axiosError?.response?.data) {
          const detail = axiosError.response.data.detail
          if (typeof detail === 'string') {
            errorMessage = detail
          } else if (Array.isArray(detail) && detail[0]?.msg) {
            errorMessage = detail[0].msg as string
          }
        }

        onUploadError?.(errorMessage)
      } finally {
        setUploading(false)
        setUploadingFile('')
      }
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
    e.target.value = ''
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileInput}
        className="hidden"
        disabled={uploading}
      />

      {/* Drag and drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-4 border-dashed rounded-xl p-12
          transition-all duration-200
          ${isDragging ? 'border-blue-900 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onClick={!uploading ? handleButtonClick : undefined}
      >
        <div className="flex flex-col items-center text-center">
          {/* Icon */}
          <div className="text-7xl mb-6" role="img" aria-label="Upload">
            {uploading ? '⏳' : '📷'}
          </div>

          {/* Instructions */}
          {uploading ? (
            <div>
              <h3 className="text-2xl font-semibold text-gray-800 mb-3">
                Uploading Photo...
              </h3>
              <p className="text-xl text-gray-600">{uploadingFile}</p>
            </div>
          ) : (
            <div>
              <h3 className="text-2xl font-semibold text-gray-800 mb-3">
                Upload Your Photos
              </h3>
              <p className="text-xl text-gray-600 mb-6 max-w-lg">
                Drag and drop photos here, or click the button below to select files
              </p>
              <LargeButton variant="primary" size="large" disabled={uploading}>
                Choose Photos
              </LargeButton>
              <p className="text-lg text-gray-500 mt-4">
                Supported formats: JPEG, PNG, GIF, WEBP (Max 20MB each)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
