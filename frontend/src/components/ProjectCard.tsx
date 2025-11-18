import React from 'react'
import { Link } from 'react-router-dom'
import type { Project } from '../api/types'

interface Props {
  project: Project
}

export const ProjectCard: React.FC<Props> = ({ project }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-primary-600">{project.category}</span>
          {project.featured && <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">Featured</span>}
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">{project.title}</h3>
        <p className="text-gray-600 mb-4 line-clamp-3">{project.description}</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {project.tags.map((tag) => (
            <span key={tag} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
              {tag}
            </span>
          ))}
        </div>
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <Link to={`/projects/${project.slug}`} className="text-primary-600 hover:text-primary-800 text-sm font-medium">
          View details
        </Link>
        {project.repo_url && (
          <a href={project.repo_url} className="text-sm text-gray-500 hover:text-gray-700" target="_blank" rel="noreferrer">
            Repository
          </a>
        )}
      </div>
    </div>
  )
}
