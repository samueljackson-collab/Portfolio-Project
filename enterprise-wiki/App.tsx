import React, { useMemo, useState, useEffect } from 'react';
import { PROJECTS } from './constants';
import { useHashRoute } from './hooks/useHashRoute';
import { useToast } from './hooks/useToast';
import { useAnalytics } from './hooks/useAnalytics';
import { useKeyboard } from './hooks/useKeyboard';
import { LS } from './utils';
import type { Settings, Project } from './types';

import Sidebar from './components/Sidebar';
import ToastContainer from './components/ToastContainer';
import AdvancedSearch from './components/AdvancedSearch';
import PortfolioPage from './pages/PortfolioPage';
import DocsPage from './pages/DocsPage';
import LearningPage from './pages/LearningPage';
import SkillsPage from './pages/SkillsPage';
import InterviewPage from './pages/InterviewPage';
import SettingsPage from './pages/SettingsPage';
import KPIDashboard from './components/KPIDashboard';
import ReferencePage from './pages/ReferencePage';

const App: React.FC = () => {
  const [route, navigate] = useHashRoute();
  const { toasts, show, dismiss } = useToast();
  const { trackEvent } = useAnalytics();
  const [searchQuery, setSearchQuery] = useState('');
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [settings, setSettings] = useState<Settings>(() => LS.get('wiki.settings', {
    wikiBaseUrl: '',
    wikiProjectsBasePath: '/projects',
    docsSubdir: 'wiki'
  }));

  // Keyboard shortcuts
  useKeyboard([
    {
      key: 'k',
      ctrl: true,
      handler: () => setShowAdvancedSearch(true),
      description: 'Open search'
    },
    {
      key: 'Escape',
      handler: () => setShowAdvancedSearch(false),
      description: 'Close search'
    }
  ]);

  useEffect(() => {
    LS.set('wiki.settings', settings);
  }, [settings]);

  const filteredProjects = useMemo(() => {
    if (!searchQuery) return PROJECTS;
    const q = searchQuery.toLowerCase();
    return PROJECTS.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.folder.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.technologies.some(t => t.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  const handleProjectSelect = (project: Project) => {
    trackEvent({
      category: 'Navigation',
      action: 'search_select_project',
      label: project.folder
    });
    navigate(`/project/${project.folder}`);
  };

  const renderPage = () => {
    switch(route.page) {
      case 'docs': return <DocsPage projects={filteredProjects} toast={{ show, dismiss, toasts }} />;
      case 'learning': return <LearningPage projects={PROJECTS} toast={{ show, dismiss, toasts }} />;
      case 'skills': return <SkillsPage projects={PROJECTS} />;
      case 'interview': return <InterviewPage projects={PROJECTS} />;
      case 'reference': return <ReferencePage />;
      case 'settings': return <SettingsPage settings={settings} setSettings={setSettings} toast={{ show, dismiss, toasts }} />;
      case 'portfolio':
      default:
        return <PortfolioPage projects={filteredProjects} totalProjects={PROJECTS.length} route={route} navigate={navigate} toast={{ show, dismiss, toasts }} settings={settings} />;
    }
  }

  return (
    <div className="min-h-screen text-slate-100 bg-cover bg-fixed bg-[#0a0f1a]" style={{
      backgroundImage: `
        radial-gradient(ellipse 100% 80% at 20% 0%, rgba(59, 130, 246, 0.12), transparent 50%),
        radial-gradient(ellipse 80% 60% at 80% 10%, rgba(139, 92, 246, 0.10), transparent 50%),
        radial-gradient(ellipse 60% 50% at 50% 100%, rgba(34, 197, 94, 0.06), transparent 50%)
      `
    }}>
      <div className="grid lg:grid-cols-[300px_1fr]">
        <Sidebar route={route} projects={PROJECTS} searchQuery={searchQuery} setSearchQuery={setSearchQuery} onAdvancedSearch={() => setShowAdvancedSearch(true)} />
        <main className="p-4 sm:p-6 min-w-0">
          {(route.page === 'portfolio' || !route.page) && <KPIDashboard projects={PROJECTS} />}
          {renderPage()}
          <footer className="mt-8 pt-5 text-center text-xs text-slate-500 border-t border-slate-700/50">
            © 2025 Sam Jackson • Enterprise Portfolio Wiki v5 • 22 Projects • 176 Docs
            <div className="mt-2 text-slate-600">
              Press <kbd className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-400">Ctrl+K</kbd> for advanced search
            </div>
          </footer>
        </main>
      </div>
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
      {showAdvancedSearch && (
        <AdvancedSearch
          projects={PROJECTS}
          onSelectProject={handleProjectSelect}
          onClose={() => setShowAdvancedSearch(false)}
        />
      )}
    </div>
  );
};

export default App;
