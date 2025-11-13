import React, { useMemo } from 'react'
import { PortfolioProfile, Project } from '../../data/portfolioData'
import { CodeIcon, FolderIcon, TerminalIcon } from './icons'

interface WelcomeScreenProps {
  profile: PortfolioProfile
  projects: Project[]
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ profile, projects }) => {
  const totalCategories = useMemo(() => new Set(projects.map(project => project.category)).size, [projects])
  const artifactCount = useMemo(
    () => projects.reduce((sum, project) => sum + project.technicalImpl.length + 2, 0),
    [projects],
  )

  return (
    <div className="p-6 sm:p-10 flex items-center justify-center h-full">
      <div className="text-center max-w-3xl">
        <div className="w-32 h-32 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-6xl font-bold mb-6 mx-auto">
          {profile.name.charAt(0)}
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Welcome to the Portfolio of {profile.name}</h1>
        <p className="text-lg text-gray-400 mb-8">{profile.summary}</p>
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Portfolio Overview</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-sky-500/10 rounded-lg text-sky-400">
                <FolderIcon />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{projects.length}</p>
                <p className="text-sm text-gray-400">Total Projects</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-400">
                <CodeIcon />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{totalCategories}</p>
                <p className="text-sm text-gray-400">Core Disciplines</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
                <TerminalIcon />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{artifactCount}</p>
                <p className="text-sm text-gray-400">Enterprise Artifacts</p>
              </div>
            </div>
          </div>
        </div>
        <p className="mt-8 text-gray-500">Select a project from the sidebar to view its details.</p>
      </div>
    </div>
  )
}
