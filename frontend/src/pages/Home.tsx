import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectService } from '../api/projects'
import type { Project } from '../api/types'
import { ProjectCard } from '../components'

export const Home: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const data = await projectService.list()
        setProjects(data.slice(0, 6))
      } catch (err) {
        console.error(err)
        setError('Failed to load projects')
      } finally {
        setLoading(false)
      }
    }

    loadProjects()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-16">
          <p className="text-sm uppercase tracking-wide text-primary-100 mb-2">Portfolio Platform</p>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Full-stack projects in one place</h1>
          <p className="text-lg text-primary-100 max-w-3xl">
            Explore reproducible DevOps, data, and AI builds backed by a FastAPI API and a React front-end.
          </p>
          <div className="mt-8 flex gap-4">
            <Link to="/projects" className="btn-primary bg-white text-primary-700 hover:bg-gray-100">
              View Projects
            </Link>
            <Link to="/login" className="btn-secondary border border-white text-white hover:bg-white hover:text-primary-700">
              Admin Login
            </Link>
          </div>
        </div>
      </header>

      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Featured work</h2>
          <Link to="/projects" className="text-primary-600 hover:text-primary-800 text-sm font-medium">
            See all projects
          </Link>
        </div>
        {loading && <div className="text-gray-500">Loading projects...</div>}
        {error && <div className="text-red-600">{error}</div>}
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
