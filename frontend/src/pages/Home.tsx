/**
 * Home Page
 *
 * Landing page with public content display
 */

import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { contentService, type Content } from '../api'
import { ContentCard } from '../components'

export const Home: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchContents = async () => {
      try {
        setIsLoading(true)
        const data = await contentService.getAll(0, 10)
        // Filter to show only published content on home page
        setContents(data.filter(item => item.is_published))
      } catch (err) {
        setError('Failed to load content')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchContents()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Welcome to Portfolio
          </h1>
          <p className="text-xl mb-8 text-primary-100">
            A modern portfolio application built with React and FastAPI
          </p>
          <div className="flex space-x-4">
            <Link to="/register" className="btn-primary bg-white text-primary-600 hover:bg-gray-100">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary bg-primary-700 text-white hover:bg-primary-600">
              Login
            </Link>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">
          Latest Content
        </h2>

        {isLoading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {!isLoading && !error && contents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No content available yet. Be the first to create some!
            </p>
          </div>
        )}

        {!isLoading && !error && contents.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contents.map((content) => (
              <ContentCard key={content.id} content={content} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
