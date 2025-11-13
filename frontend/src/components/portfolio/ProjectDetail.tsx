import React, { useEffect, useState } from 'react'
import { Project } from '../../data/portfolioData'
import { BookIcon, CodeIcon, FileTextIcon, TerminalIcon } from './icons'
import { CodeBlock } from './CodeBlock'

export const ProjectDetail: React.FC<{ project: Project }> = ({ project }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'operational' | 'strategic'>('overview')

  useEffect(() => {
    setActiveTab('overview')
  }, [project.id])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <FileTextIcon /> },
    { id: 'technical', label: 'Technical Implementation', icon: <CodeIcon /> },
    { id: 'operational', label: 'Operational Materials', icon: <TerminalIcon /> },
    { id: 'strategic', label: 'Strategic Documents', icon: <BookIcon /> },
  ] as const

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{project.description}</p>
      case 'technical':
        return project.technicalImpl.map(impl => <CodeBlock key={impl.fileName} {...impl} />)
      case 'operational':
        return (
          <div className="prose prose-invert prose-sm max-w-none bg-gray-800 border border-gray-700 p-6 rounded-lg">
            <h3 className="text-sky-400">{project.operationalMats.title}</h3>
            <pre className="whitespace-pre-wrap font-sans text-gray-300">{project.operationalMats.content}</pre>
          </div>
        )
      case 'strategic':
        return (
          <div className="prose prose-invert prose-sm max-w-none bg-gray-800 border border-gray-700 p-6 rounded-lg">
            <h3 className="text-sky-400">{project.strategicDocs.title}</h3>
            <pre className="whitespace-pre-wrap font-sans text-gray-300">{project.strategicDocs.content}</pre>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="p-6 sm:p-10">
      <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">{project.title}</h1>
      <p className="text-base text-sky-400 mb-8">{project.category}</p>

      <div className="border-b border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-2 sm:space-x-4 overflow-x-auto" aria-label="Tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap flex items-center gap-2 py-3 px-1 sm:px-3 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-sky-500 text-sky-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="animate-fade-in">{renderContent()}</div>
    </div>
  )
}
