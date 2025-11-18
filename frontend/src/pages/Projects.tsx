import React, { useEffect, useState } from 'react'
import { projectService } from '../api/projects'
import type { Project } from '../api/types'
import { ProjectCard } from '../components'

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await projectService.list()
        setProjects(data)
      } catch (err) {
        setError('Unable to load projects')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-gray-500 uppercase tracking-wide">Projects</p>
          <h1 className="text-3xl font-bold text-gray-900">Full portfolio catalog</h1>
        </div>
      </div>
      {loading && <div className="text-gray-500">Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  )
}
