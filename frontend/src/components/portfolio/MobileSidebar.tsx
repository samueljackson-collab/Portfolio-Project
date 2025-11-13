import React, { useMemo } from 'react'
import { PortfolioProfile, Project, ProjectGroups } from '../../data/portfolioData'
import { FolderIcon, HomeIcon } from './icons'

interface MobileSidebarProps {
  profile: PortfolioProfile
  projects: Project[]
  selectedProjectId: string | null
  isSidebarOpen: boolean
  onSelectProject: (id: string | null) => void
  onClose: () => void
}

export const MobileSidebar: React.FC<MobileSidebarProps> = ({
  profile,
  projects,
  selectedProjectId,
  isSidebarOpen,
  onSelectProject,
  onClose,
}) => {
  const groupedProjects = useMemo<ProjectGroups>(() => {
    return projects.reduce<ProjectGroups>((acc, project) => {
      if (!acc[project.category]) {
        acc[project.category] = []
      }
      acc[project.category].push(project)
      return acc
    }, {})
  }, [projects])

  return (
    <div className={`fixed inset-0 z-40 md:hidden transition-transform transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className="fixed inset-0 bg-black/60" onClick={onClose}></div>
      <div className="relative w-80 max-w-[calc(100%-3rem)] bg-gray-900 text-white p-6 h-full overflow-y-auto border-r border-gray-800">
        <div className="flex flex-col items-center text-center pb-6 border-b border-gray-700">
          <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-4xl font-bold mb-4">
            {profile.name.charAt(0)}
          </div>
          <h1 className="text-xl font-bold">{profile.name}</h1>
          <p className="text-sm text-gray-400">{profile.title}</p>
        </div>
        <nav className="mt-6">
          <ul>
            <li>
              <button
                type="button"
                onClick={() => {
                  onSelectProject(null)
                  onClose()
                }}
                className={`flex items-center w-full text-left py-2 px-3 rounded-md hover:bg-gray-700 transition-colors ${!selectedProjectId ? 'bg-sky-600' : ''}`}
              >
                <HomeIcon />
                <span className="ml-3">Portfolio Home</span>
              </button>
            </li>
          </ul>
          <div className="mt-6">
            {Object.keys(groupedProjects).map(category => (
              <div key={category} className="mb-6">
                <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">{category}</h2>
                <ul>
                  {groupedProjects[category].map(project => (
                    <li key={project.id}>
                      <button
                        type="button"
                        onClick={() => {
                          onSelectProject(project.id)
                          onClose()
                        }}
                        className={`flex items-center w-full text-left py-2 px-3 rounded-md text-sm hover:bg-gray-700 transition-colors ${selectedProjectId === project.id ? 'bg-gray-700 font-semibold' : ''}`}
                      >
                        <FolderIcon />
                        <span className="ml-3 truncate">{project.title}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </nav>
      </div>
    </div>
  )
}
