import React, { useState } from 'react';
import {
  Book,
  Server,
  GitBranch,
  TestTube,
  Network,
  ChevronRight,
  FileText,
  Code,
  Shield,
  Activity,
  CheckCircle,
} from 'lucide-react';
import clsx from 'clsx';
import { roleLearningPaths } from '../private/roleLearningPaths.js';

const roleThemes = {
  sde: {
    accentBg: 'bg-blue-600',
    accentHover: 'hover:bg-blue-700',
  },
  devops: {
    accentBg: 'bg-green-600',
    accentHover: 'hover:bg-green-700',
  },
  qa: {
    accentBg: 'bg-purple-600',
    accentHover: 'hover:bg-purple-700',
  },
  architect: {
    accentBg: 'bg-orange-500',
    accentHover: 'hover:bg-orange-600',
  },
};

const roles = {
  sde: {
    title: 'System Development Engineer',
    icon: Server,
    theme: roleThemes.sde,
    description: 'Infrastructure, automation, and system reliability',
    weeks: 8,
  },
  devops: {
    title: 'DevOps Engineer',
    icon: GitBranch,
    theme: roleThemes.devops,
    description: 'CI/CD, GitOps, and deployment automation',
    weeks: 6,
  },
  qa: {
    title: 'QA Engineer III',
    icon: TestTube,
    theme: roleThemes.qa,
    description: 'Testing strategy, automation, and quality assurance',
    weeks: 6,
  },
  architect: {
    title: 'Solutions Architect',
    icon: Network,
    theme: roleThemes.architect,
    description: 'System design, architecture patterns, and trade-offs',
    weeks: 8,
  },
};

// Role-specific learning plans (responsibilities, skills, week-by-week breakdowns) are stored in
// src/private/roleLearningPaths.js so the UI layer here can focus on presentation and behavior.

// The EnterpriseWiki component coordinates role selection with the detailed timeline view.
// Local state tracks which role/week is active while the layout renders responsive Tailwind sections.
const EnterpriseWiki = () => {
  const [selectedRole, setSelectedRole] = useState('sde');
  const [selectedWeek, setSelectedWeek] = useState(1);

  const currentRole = roles[selectedRole];
  const currentContent = roleLearningPaths[selectedRole];
  const RoleIcon = currentRole.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 mb-8 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <Book className="w-12 h-12 text-white" />
            <h1 className="text-4xl font-bold text-white">Enterprise Portfolio Wiki</h1>
          </div>
          <p className="text-blue-100 text-lg">Complete learning paths for all technical roles</p>
        </div>

        {/* Split layout: left column for navigation, right column for the active curriculum detail. */}
        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            {/* Role selector lists every persona with consistent styling and click handlers. */}
            <div className="bg-slate-800 rounded-xl p-6 shadow-xl sticky top-4">
              <h2 className="text-xl font-bold text-white mb-4">Select Role</h2>
              <div className="space-y-3">
                {Object.entries(roles).map(([key, role]) => {
                  const Icon = role.icon;
                  const { accentBg } = role.theme;

                  return (
                    <button
                      type="button"
                      key={key}
                      onClick={() => {
                        setSelectedRole(key);
                        setSelectedWeek(1);
                      }}
                      className={clsx(
                        'w-full p-4 rounded-lg transition-all',
                        selectedRole === key
                          ? [accentBg, 'text-white shadow-lg scale-105']
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-6 h-6" />
                        <div className="text-left">
                          <div className="font-semibold">{role.title}</div>
                          <div className="text-xs opacity-80">{role.weeks} weeks</div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="mt-6 pt-6 border-t border-slate-700">
                <h3 className="text-sm font-semibold text-slate-400 mb-3">Your Progress</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>
                      Week {selectedWeek} of {currentRole.weeks}
                    </span>
                    <span>{Math.round((selectedWeek / currentRole.weeks) * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={clsx(currentRole.theme.accentBg, 'h-2 rounded-full transition-all')}
                      style={{ width: `${(selectedWeek / currentRole.weeks) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-slate-800 rounded-xl p-6 mb-6 shadow-xl">
              <div className="flex items-center gap-4 mb-4">
                <div className={clsx('p-3 rounded-lg', currentRole.theme.accentBg)}>
                  <RoleIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{currentRole.title}</h2>
                  <p className="text-slate-400">{currentRole.description}</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6 mt-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    Key Responsibilities
                  </h3>
                  <ul className="space-y-2">
                    {currentContent.overview.responsibilities.map((resp, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
                        {resp}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Code className="w-5 h-5 text-purple-500" />
                    Core Skills
                  </h3>
                  <ul className="space-y-2">
                    {currentContent.overview.skills.map((skill, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                        <ChevronRight className="w-4 h-4 text-purple-500 mt-1 flex-shrink-0" />
                        {skill}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl p-6 mb-6 shadow-xl">
              <h3 className="text-xl font-bold text-white mb-4">Learning Path Timeline</h3>
              {/* Week selector behaves like tabs, keeping the selected week in sync with the detail card below. */}
              <div className="flex gap-2 overflow-x-auto pb-2">
                {currentContent.weeks.map((week) => (
                  <button
                    type="button"
                    key={week.number}
                    onClick={() => setSelectedWeek(week.number)}
                    className={clsx(
                      'px-4 py-2 rounded-lg whitespace-nowrap transition-all',
                      selectedWeek === week.number
                        ? [currentRole.theme.accentBg, 'text-white shadow-lg']
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    )}
                  >
                    Week {week.number}
                  </button>
                ))}
              </div>
            </div>

            {currentContent.weeks
              .filter((week) => week.number === selectedWeek)
              .map((week) => (
                <div key={week.number} className="bg-slate-800 rounded-xl p-6 shadow-xl">
                  {/* Header summarises the currently focused week and shows a quick status pill. */}
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-bold text-white">
                        Week {week.number}: {week.title}
                      </h3>
                      <p className="text-slate-400 mt-1">Duration: 5-7 days</p>
                    </div>
                    <div className={clsx('px-4 py-2 rounded-lg', currentRole.theme.accentBg)}>
                      <span className="text-white font-semibold">In Progress</span>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-500" />
                        Topics Covered
                      </h4>
                      <ul className="space-y-2">
                        {week.topics.map((topic, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <div
                              className={clsx(
                                'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5',
                                currentRole.theme.accentBg
                              )}
                            >
                              <span className="text-white text-xs font-bold">{idx + 1}</span>
                            </div>
                            <span className="text-slate-300">{topic}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        Deliverables
                      </h4>
                      <ul className="space-y-2">
                        {week.deliverables.map((deliverable, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                            <span className="text-slate-300">{deliverable}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Action buttons provide obvious next steps without wiring specific navigation yet. */}
                  <div className="mt-6 pt-6 border-t border-slate-700 flex gap-4 flex-col sm:flex-row">
                    <button
                      type="button"
                      className={clsx(
                        'flex-1 py-3 px-6 text-white rounded-lg font-semibold transition-colors',
                        currentRole.theme.accentBg,
                        currentRole.theme.accentHover
                      )}
                    >
                      View Detailed Guide
                    </button>
                    <button
                      type="button"
                      className="py-3 px-6 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition-colors"
                    >
                      Access Resources
                    </button>
                  </div>
                </div>
              ))}

            <div className="grid md:grid-cols-3 gap-4 mt-6">
              <div className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors cursor-pointer">
                <Code className="w-8 h-8 text-blue-500 mb-2" />
                <h4 className="font-semibold text-white">Code Examples</h4>
                <p className="text-sm text-slate-400">Full implementation samples</p>
              </div>
              <div className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors cursor-pointer">
                <Activity className="w-8 h-8 text-green-500 mb-2" />
                <h4 className="font-semibold text-white">Live Demos</h4>
                <p className="text-sm text-slate-400">Interactive tutorials</p>
              </div>
              <div className="bg-slate-800 rounded-xl p-4 hover:bg-slate-700 transition-colors cursor-pointer">
                <Shield className="w-8 h-8 text-purple-500 mb-2" />
                <h4 className="font-semibold text-white">Best Practices</h4>
                <p className="text-sm text-slate-400">Industry standards</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseWiki;
