/**
 * Dashboard Page
 *
 * Authenticated user dashboard with content management
 */

import React, { useCallback, useEffect, useState } from 'react'
import { contentService, type Content, type CreateContentRequest } from '../api'
import { ContentCard } from '../components'
import { useAuth } from '../context'

export const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [contents, setContents] = useState<Content[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  // Form state
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchContents = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await contentService.getAll()
      // Filter to show only current user's content
      setContents(data.filter((item) => item.owner_id === user?.id))
    } catch (err) {
      setError('Failed to load content')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }, [user?.id])

  useEffect(() => {
    fetchContents()
  }, [fetchContents])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const data: CreateContentRequest = {
        title,
        body: body || undefined,
        is_published: isPublished,
      }

      await contentService.create(data)

      // Reset form
      setTitle('')
      setBody('')
      setIsPublished(false)
      setShowCreateForm(false)

      // Refresh content list
      await fetchContents()
    } catch (err) {
      setError('Failed to create content')
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this content?')) {
      return
    }

    try {
      await contentService.delete(id)
      await fetchContents()
    } catch (err) {
      setError('Failed to delete content')
      console.error(err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            My Dashboard
          </h1>
          <p className="text-gray-600">
            Welcome back, {user?.email}
          </p>
        </div>

        {/* Create Button */}
        <div className="mb-8">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-primary"
          >
            {showCreateForm ? 'Cancel' : 'Create New Content'}
          </button>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="card mb-8">
            <h2 className="text-xl font-semibold mb-4">Create New Content</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                  Title
                </label>
                <input
                  id="title"
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="input-field"
                  placeholder="Enter content title"
                />
              </div>

              <div>
                <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
                  Body
                </label>
                <textarea
                  id="body"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="input-field"
                  rows={5}
                  placeholder="Enter content body"
                />
              </div>

              <div className="flex items-center">
                <input
                  id="published"
                  type="checkbox"
                  checked={isPublished}
                  onChange={(e) => setIsPublished(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="published" className="ml-2 block text-sm text-gray-900">
                  Publish immediately
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-primary"
                >
                  {isSubmitting ? 'Creating...' : 'Create Content'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-8">
            {error}
          </div>
        )}

        {/* Content List */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            My Content ({contents.length})
          </h2>

          {isLoading && (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          )}

          {!isLoading && contents.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                No content yet. Create your first content item!
              </p>
            </div>
          )}

          {!isLoading && contents.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contents.map((content) => (
                <ContentCard
                  key={content.id}
                  content={content}
                  onDelete={handleDelete}
                  showActions={true}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
