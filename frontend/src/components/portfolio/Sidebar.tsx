import React from 'react'
import { PortfolioProfile, Project, ProjectGroups } from '../../data/portfolioData'
import { FolderIcon, HomeIcon } from './icons'

interface SidebarProps {
  profile: PortfolioProfile
  groupedProjects: ProjectGroups
  selectedProjectId: string | null
  onSelectProject: (id: string | null) => void
}

export const Sidebar: React.FC<SidebarProps> = ({ profile, groupedProjects, selectedProjectId, onSelectProject }) => (
  <aside className="w-80 bg-gray-900 text-white p-6 fixed h-full overflow-y-auto border-r border-gray-800 hidden md:block">
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
            onClick={() => onSelectProject(null)}
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
              {groupedProjects[category].map((project: Project) => (
                <li key={project.id}>
                  <button
                    type="button"
                    onClick={() => onSelectProject(project.id)}
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
  </aside>
)
