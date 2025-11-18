import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { projectService } from '../api/projects'
import type { Project } from '../api/types'

export const ProjectDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      if (!slug) return
      try {
        const data = await projectService.get(slug)
        setProject(data)
      } catch (err) {
        setError('Project not found')
      }
    }
    load()
  }, [slug])

  if (error) return <div className="max-w-4xl mx-auto px-4 py-8 text-red-600">{error}</div>
  if (!project) return <div className="max-w-4xl mx-auto px-4 py-8">Loading...</div>

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <p className="text-sm text-gray-500 uppercase tracking-wide">{project.category}</p>
      <h1 className="text-3xl font-bold text-gray-900 mb-4">{project.title}</h1>
      <p className="text-gray-700 mb-6">{project.description}</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {project.tags.map((tag) => (
          <span key={tag} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
            {tag}
          </span>
        ))}
      </div>
      <div className="space-y-2">
        {project.repo_url && (
          <a href={project.repo_url} target="_blank" rel="noreferrer" className="text-primary-600 hover:text-primary-800">
            Repository
          </a>
        )}
        {project.live_url && (
          <a href={project.live_url} target="_blank" rel="noreferrer" className="block text-primary-600 hover:text-primary-800">
            Live Demo
          </a>
        )}
      </div>
    </div>
  )
}
