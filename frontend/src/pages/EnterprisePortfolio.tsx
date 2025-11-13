import React, { useCallback, useMemo, useState } from 'react'
import { MobileSidebar, ProjectDetail, Sidebar, WelcomeScreen } from '../components/portfolio'
import { portfolioData, Project, ProjectGroups } from '../data/portfolioData'
import './EnterprisePortfolio.css'

export const EnterprisePortfolio: React.FC = () => {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const groupedProjects = useMemo<ProjectGroups>(() => {
    return portfolioData.projects.reduce<ProjectGroups>((acc, project) => {
      if (!acc[project.category]) {
        acc[project.category] = []
      }
      acc[project.category].push(project)
      return acc
    }, {})
  }, [])

  const selectedProject = useMemo<Project | null>(() => {
    if (!selectedProjectId) {
      return null
    }
    return portfolioData.projects.find(project => project.id === selectedProjectId) ?? null
  }, [selectedProjectId])

  const handleSelectProject = useCallback((projectId: string | null) => {
    setSelectedProjectId(projectId)
    setIsSidebarOpen(false)
  }, [])

  return (
    <div className="bg-gray-950 text-gray-100 min-h-screen">
      <Sidebar
        profile={portfolioData.profile}
        groupedProjects={groupedProjects}
        selectedProjectId={selectedProjectId}
        onSelectProject={handleSelectProject}
      />

      <div className="md:ml-80 min-h-screen">
        <header className="md:hidden flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900">
          <div>
            <p className="text-xs text-gray-400">Portfolio Showcase</p>
            <p className="text-lg font-semibold text-white">{selectedProject?.title ?? portfolioData.profile.name}</p>
          </div>
          <button
            type="button"
            onClick={() => setIsSidebarOpen(true)}
            className="px-4 py-2 rounded-md bg-sky-600 text-white text-sm font-semibold"
          >
            Browse Projects
          </button>
        </header>

        {selectedProject ? (
          <ProjectDetail project={selectedProject} />
        ) : (
          <WelcomeScreen profile={portfolioData.profile} projects={portfolioData.projects} />
        )}
      </div>

      <MobileSidebar
        profile={portfolioData.profile}
        projects={portfolioData.projects}
        selectedProjectId={selectedProjectId}
        isSidebarOpen={isSidebarOpen}
        onSelectProject={handleSelectProject}
        onClose={() => setIsSidebarOpen(false)}
      />
    </div>
  )
}
