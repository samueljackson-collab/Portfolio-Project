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
import { isAxiosError } from 'axios'
import { photoService } from '../../api/services'
import type { PhotoUploadResponse } from '../../api/types'
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

  const handleFiles = async (files: File[] | null) => {
    if (!files || files.length === 0) return

    for (const file of files) {

      // Validate file type
      if (!file.type.startsWith('image/')) {
        onUploadError?.(`${file.name} is not an image file`)
        continue
      }

      // Validate file size (20MB max)
      if (file.size > 20 * 1024 * 1024) {
        onUploadError?.(`${file.name} is too large. Maximum size is 20MB.`)
        continue
      }

      try {
        setUploading(true)
        setUploadingFile(file.name)

        const response = await photoService.upload(file)
        onUploadComplete?.(response)
      } catch (error) {
        let errorMessage = 'Failed to upload photo'

        if (isAxiosError(error)) {
          const detail = (error.response?.data as { detail?: unknown })?.detail
          if (typeof detail === 'string') {
            errorMessage = detail
          } else if (Array.isArray(detail) && detail.length > 0) {
            const first = detail[0] as { msg?: unknown }
            if (first?.msg && typeof first.msg === 'string') {
              errorMessage = first.msg
            }
          }
        } else if (error instanceof Error) {
          errorMessage = error.message
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
    void handleFiles(Array.from(e.dataTransfer.files))
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : null
    void handleFiles(files)
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
          ${isDragging ? 'border-blue-900 bg-blue-100' : 'border-gray-300 bg-gray-50'}
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
              <LargeButton
                variant="primary"
                size="large"
                disabled={uploading}
                onClick={handleButtonClick}
                type="button"
              >
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
