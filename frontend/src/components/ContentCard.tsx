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

  const statusClasses = content.is_published
    ? 'bg-emerald-500/15 text-emerald-100 border-emerald-500/30'
    : 'bg-amber-500/15 text-amber-100 border-amber-500/30'
  const statusDotClass = content.is_published ? 'bg-emerald-300' : 'bg-amber-300'
  const statusLabel = content.is_published ? 'Published' : 'Draft'

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80 p-6 text-slate-50 shadow-2xl shadow-slate-900/40 backdrop-blur-xl transition duration-200 hover:-translate-y-1 hover:shadow-primary-500/30">
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-500/10 via-slate-900/40 to-fuchsia-500/10" />

      {/* Header */}
      <div className="relative flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary-100/80">
            Workspace item
          </p>
          <h3 className="text-xl font-semibold text-white">
            {content.title}
          </h3>
          <div className="flex items-center gap-3 text-sm text-slate-300">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-primary-300" />
              Created {formatDate(content.created_at)}
            </span>
            <span
              className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${statusClasses}`}
            >
              <span className={`h-2 w-2 rounded-full ${content.is_published ? 'bg-emerald-300' : 'bg-amber-300'}`} />
              {statusLabel}
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      {content.body && (
        <div className="relative mt-4">
          <p className="text-sm text-slate-200/90 line-clamp-3">
            {content.body}
          </p>
        </div>
      )}

      {/* Actions */}
      {showActions && (onEdit || onDelete) && (
        <div className="relative mt-6 flex items-center justify-end gap-2 border-t border-white/10 pt-4">
          {onEdit && (
            <button
              onClick={() => onEdit(content)}
              className="rounded-lg border border-white/20 px-3 py-1.5 text-sm font-semibold text-slate-100 transition hover:border-primary-300 hover:text-white"
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(content.id)}
              className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-1.5 text-sm font-semibold text-red-100 transition hover:border-red-300 hover:bg-red-500/20"
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  )
}
