import React from 'react';
import { REPO } from '../constants';
import type { Project, HashRoute } from '../types';
import { cn } from '../utils';

interface SidebarProps {
  route: HashRoute;
  projects: Project[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onAdvancedSearch?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ route, projects, searchQuery, setSearchQuery, onAdvancedSearch }) => {
  const stats = {
    projects: projects.length,
    docs: projects.length * 8,
    done: projects.filter(p => p.status === 'Done').length
  };

  const navItems = [
    { id: 'portfolio', icon: '📁', label: 'Portfolio', badge: stats.projects },
    { id: 'docs', icon: '📚', label: 'Documentation', badge: stats.docs },
    { id: 'learning', icon: '🎓', label: 'Learning Paths', badge: 4 },
    { id: 'skills', icon: '💡', label: 'Skills Matrix' },
    { id: 'interview', icon: '🎯', label: 'Interview Prep' },
    { id: 'reference', icon: '🔖', label: 'Reference' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  return (
    <aside className="sticky top-0 z-10 flex h-auto flex-col overflow-y-auto border-b border-slate-700/50 bg-slate-900/80 p-5 backdrop-blur-md lg:h-screen lg:border-b-0 lg:border-r">
      <div className="mb-4 flex items-center gap-3 border-b border-slate-700/50 pb-4">
        <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-400 via-emerald-400 to-purple-400 text-2xl font-black text-slate-900 shadow-md shadow-blue-500/10">
          SJ
        </div>
        <div>
          <h1 className="text-base font-bold tracking-tight">Portfolio Wiki</h1>
          <p className="text-xs text-slate-400">Sam Jackson</p>
        </div>
      </div>

      <div className="mb-4 space-y-2">
        <div className="relative">
          <input
            className="w-full rounded-lg border border-slate-700/50 bg-black/20 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-blue-400/50 focus:outline-none focus:ring-2 focus:ring-blue-400/20"
            type="text"
            placeholder="Quick search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        {onAdvancedSearch && (
          <button
            onClick={onAdvancedSearch}
            className="w-full rounded-lg border border-slate-700/50 bg-black/20 px-3 py-2 text-sm text-slate-400 transition-colors hover:border-blue-400/50 hover:bg-white/5 hover:text-slate-100"
          >
            🔍 Advanced Search <kbd className="ml-auto rounded bg-slate-800 px-1.5 py-0.5 text-xs">Ctrl+K</kbd>
          </button>
        )}
      </div>

      <nav className="mb-4">
        <div className="mb-2 pl-2 text-xs font-semibold uppercase tracking-widest text-slate-500">Navigation</div>
        <div className="flex flex-col gap-0.5">
          {navItems.map(item => (
            <a
              key={item.id}
              href={`#/${item.id}`}
              className={cn(
                'flex items-center justify-between rounded-lg border border-transparent px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-white/5 hover:text-slate-100',
                (route.page === item.id || (!route.page && item.id === 'portfolio')) && 'border-blue-400/30 bg-blue-500/10 text-slate-100'
              )}
            >
              <span className="flex items-center gap-2">
                <span className="w-5 text-center text-base">{item.icon}</span>
                {item.label}
              </span>
              {item.badge && <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs font-medium text-slate-500">{item.badge}</span>}
            </a>
          ))}
        </div>
      </nav>

      <div className="mt-auto border-t border-slate-700/50 pt-4">
        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-lg border border-slate-700/50 bg-white/5 p-3 text-center">
            <div className="text-xl font-extrabold bg-gradient-to-br from-blue-400 to-emerald-400 bg-clip-text text-transparent">{stats.done}</div>
            <div className="text-[9px] font-semibold uppercase tracking-wider text-slate-500">Completed</div>
          </div>
          <div className="rounded-lg border border-slate-700/50 bg-white/5 p-3 text-center">
            <div className="text-xl font-extrabold bg-gradient-to-br from-blue-400 to-emerald-400 bg-clip-text text-transparent">{stats.docs}</div>
            <div className="text-[9px] font-semibold uppercase tracking-wider text-slate-500">Docs</div>
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <a href={REPO.url} target="_blank" rel="noreferrer" className="flex-1 rounded-lg border border-slate-700/50 bg-white/5 py-2 text-center text-xs text-slate-400 transition-colors hover:border-blue-400/50 hover:bg-white/10 hover:text-slate-100">🔗 GitHub</a>
          <a href="https://linkedin.com/in/sams-jackson" target="_blank" rel="noreferrer" className="flex-1 rounded-lg border border-slate-700/50 bg-white/5 py-2 text-center text-xs text-slate-400 transition-colors hover:border-blue-400/50 hover:bg-white/10 hover:text-slate-100">💼 LinkedIn</a>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
