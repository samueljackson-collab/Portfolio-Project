import React, { useState, useMemo } from 'react';
import type { Project } from '../types';
import { cn } from '../utils';

interface AdvancedSearchProps {
  projects: Project[];
  onSelectProject: (project: Project) => void;
  onClose: () => void;
}

const fuzzyMatch = (str: string, pattern: string): boolean => {
  pattern = pattern.toLowerCase();
  str = str.toLowerCase();
  let patternIdx = 0;
  let strIdx = 0;

  while (patternIdx < pattern.length && strIdx < str.length) {
    if (pattern[patternIdx] === str[strIdx]) {
      patternIdx++;
    }
    strIdx++;
  }

  return patternIdx === pattern.length;
};

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({ projects, onSelectProject, onClose }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const results = useMemo(() => {
    if (!query.trim()) return projects.slice(0, 10);

    const scored = projects
      .map(p => {
        let score = 0;
        const q = query.toLowerCase();

        // Exact matches score highest
        if (p.title.toLowerCase().includes(q)) score += 100;
        if (p.folder.toLowerCase().includes(q)) score += 80;
        if (p.description.toLowerCase().includes(q)) score += 50;

        // Fuzzy matches
        if (fuzzyMatch(p.title, query)) score += 40;
        if (fuzzyMatch(p.folder, query)) score += 30;

        // Technology matches
        p.technologies.forEach(tech => {
          if (tech.toLowerCase().includes(q)) score += 60;
          if (fuzzyMatch(tech, query)) score += 20;
        });

        // Tags
        p.tags.forEach(tag => {
          if (tag.toLowerCase().includes(q)) score += 40;
        });

        return { project: p, score };
      })
      .filter(r => r.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
      .map(r => r.project);

    return scored;
  }, [projects, query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      e.preventDefault();
      onSelectProject(results[selectedIndex]);
      onClose();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/70 p-4 pt-20 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl rounded-xl border border-slate-700 bg-slate-800 shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        <div className="border-b border-slate-700/50 p-4">
          <input
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search projects (fuzzy matching)..."
            className="w-full bg-transparent text-lg text-slate-100 placeholder-slate-500 outline-none"
            autoFocus
          />
        </div>

        <div className="max-h-96 overflow-y-auto">
          {results.length === 0 && query && (
            <div className="p-8 text-center text-slate-500">No projects found</div>
          )}

          {results.map((p, idx) => (
            <div
              key={p.folder}
              onClick={() => {
                onSelectProject(p);
                onClose();
              }}
              className={cn(
                'cursor-pointer border-b border-slate-700/50 p-4 transition-colors last:border-b-0',
                idx === selectedIndex ? 'bg-blue-500/10' : 'hover:bg-white/5'
              )}
            >
              <div className="font-semibold text-slate-100">{p.title}</div>
              <div className="mt-1 text-sm text-slate-400 line-clamp-1">{p.description}</div>
              <div className="mt-2 flex flex-wrap gap-1">
                {p.technologies.slice(0, 5).map(t => (
                  <span key={t} className="rounded bg-white/5 px-2 py-0.5 text-xs text-slate-400">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-slate-700/50 bg-slate-900/50 px-4 py-2 text-xs text-slate-500">
          <span className="mr-4">↑↓ Navigate</span>
          <span className="mr-4">Enter Select</span>
          <span>Esc Close</span>
        </div>
      </div>
    </div>
  );
};

export default AdvancedSearch;
