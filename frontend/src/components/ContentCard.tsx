/**
 * Content Card Component
 *
 * Display component for content items
 */

import React from 'react'
import type { Content } from '../api'

interface ContentCardProps {
  content: Content
  onEdit?: (content: Content) => void
  onDelete?: (id: string) => void
  showActions?: boolean
}

export const ContentCard: React.FC<ContentCardProps> = ({
  content,
  onEdit,
  onDelete,
  showActions = false,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {content.title}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span>Created: {formatDate(content.created_at)}</span>
            <span className={`px-2 py-1 rounded-full text-xs ${
              content.is_published
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {content.is_published ? 'Published' : 'Draft'}
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      {content.body && (
        <div className="mb-4">
          <p className="text-gray-700 line-clamp-3">
            {content.body}
          </p>
        </div>
      )}

      {/* Actions */}
      {showActions && (onEdit || onDelete) && (
        <div className="flex justify-end space-x-2 pt-4 border-t">
          {onEdit && (
            <button
              onClick={() => onEdit(content)}
              className="px-3 py-1 text-sm text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded transition-colors"
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(content.id)}
              className="px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  )
}
