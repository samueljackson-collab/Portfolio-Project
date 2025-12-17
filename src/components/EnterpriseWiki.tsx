import React, { useMemo, useState } from 'react';
import {
  enterpriseWikiIcons,
  roleContent,
  roleThemes,
  resourceCards,
  roles,
} from './enterpriseWikiData';
import type {
  RoleDefinition,
  RoleKey,
  RoleTheme,
  ResourceLink,
  WeekPlan,
} from './enterpriseWikiData';

const { Book, CheckCircle, ChevronRight, Code, FileText, Shield, Activity } =
  enterpriseWikiIcons;

// Lightweight helper to assemble Tailwind class strings without pulling in a
// third-party dependency just for conditional styling.
const classNames = (
  ...classes: Array<string | false | null | undefined>
): string => classes.filter(Boolean).join(' ');

// WeekDetail keeps the weekly curriculum rendering focused and predictable.
const WeekDetail: React.FC<{
  week: WeekPlan;
  theme: RoleTheme;
}> = ({ week, theme }) => (
  <div className="bg-slate-800 rounded-xl p-6 shadow-xl">
    <div className="flex items-center justify-between mb-6">
      <div>
        <h3 className="text-2xl font-bold text-white">
          Week {week.number}: {week.title}
        </h3>
        <p className="text-slate-400 mt-1">Duration: 5-7 days</p>
      </div>
      <div className={classNames('px-4 py-2 rounded-lg', theme.accentBg)}>
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
            <li
              key={`${week.number}-topic-${idx}`}
              className="flex items-start gap-2"
            >
              <div
                className={classNames(
                  'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5',
                  theme.accentBg,
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
            <li
              key={`${week.number}-deliverable-${idx}`}
              className="flex items-start gap-2"
            >
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <span className="text-slate-300">{deliverable}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>

    <div className="mt-6 pt-6 border-t border-slate-700 flex gap-4">
      <button
        className={classNames(
          'flex-1 py-3 px-6 text-white rounded-lg font-semibold transition-colors',
          theme.accentBg,
          theme.accentHoverBg,
        )}
      >
        View Detailed Guide
      </button>
      <button className="py-3 px-6 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition-colors">
        Access Resources
      </button>
    </div>
  </div>
);

// The main component stitches metadata and curriculum content together for the
// interactive role selector view.
const EnterpriseWiki: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<RoleKey>('sde');
  const [selectedWeek, setSelectedWeek] = useState<number>(1);

  const currentRole = roles[selectedRole];
  const currentTheme = roleThemes[selectedRole];
  const currentContent = roleContent[selectedRole];
  const activeWeek = useMemo(
    () =>
      currentContent.weeks.find((week) => week.number === selectedWeek) ??
      currentContent.weeks[0],
    [currentContent.weeks, selectedWeek],
  );
  const RoleIcon = currentRole.icon;

  // Protect against rounding overshooting 100% when the last week is active.
  const progressPercentage = useMemo(
    () => Math.min(100, Math.round((selectedWeek / currentRole.weeks) * 100)),
    [selectedWeek, currentRole.weeks],
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 mb-8 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <Book className="w-12 h-12 text-white" />
            <h1 className="text-4xl font-bold text-white">Enterprise Portfolio Wiki</h1>
          </div>
          <p className="text-blue-100 text-lg">
            Complete learning paths for all technical roles
          </p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-slate-800 rounded-xl p-6 shadow-xl sticky top-4">
              <h2 className="text-xl font-bold text-white mb-4">Select Role</h2>
              <div className="space-y-3">
                {(
                  Object.entries(roles) as Array<[RoleKey, RoleDefinition]>
                ).map(([key, role]) => {
                  const Icon = role.icon;
                  const isSelected = selectedRole === key;
                  return (
                    <button
                      key={key}
                      onClick={() => {
                        setSelectedRole(key);
                        setSelectedWeek(1);
                      }}
                      className={classNames(
                        'w-full p-4 rounded-lg transition-all',
                        isSelected
                          ? roleThemes[key].selectedButton
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600',
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
                    <span>{progressPercentage}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={classNames(
                        currentTheme.accentBg,
                        'h-2 rounded-full transition-all',
                      )}
                      style={{ width: `${progressPercentage}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-slate-800 rounded-xl p-6 mb-6 shadow-xl">
              <div className="flex items-center gap-4 mb-4">
                <div className={classNames('p-3 rounded-lg', currentTheme.accentBg)}>
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
              <div className="flex gap-2 overflow-x-auto pb-2">
                {currentContent.weeks.map((week) => {
                  const isActiveWeek = selectedWeek === week.number;
                  return (
                    <button
                      key={week.number}
                      onClick={() => setSelectedWeek(week.number)}
                      className={classNames(
                        'px-4 py-2 rounded-lg whitespace-nowrap transition-all',
                        isActiveWeek
                          ? classNames(currentTheme.accentBg, 'text-white shadow-lg')
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600',
                      )}
                    >
                      Week {week.number}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Always render at least one week so the layout stays consistent. */}
            {activeWeek && <WeekDetail week={activeWeek} theme={currentTheme} />}

            <div className="grid md:grid-cols-3 gap-4 mt-6">
              {resourceCards.map((resource: ResourceLink) => {
                const Icon = resource.icon;
                return (
                  <button
                    key={resource.key}
                    type="button"
                    onClick={() =>
                      window.open(resource.href, '_blank', 'noreferrer noopener')
                    }
                    className="group bg-slate-800 rounded-xl p-4 text-left transition transform hover:-translate-y-0.5 hover:bg-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-400 focus-visible:ring-offset-slate-900"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Icon className={classNames('w-8 h-8', resource.iconColor)} />
                      <span className="text-xs font-semibold text-blue-200 opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100 transition">
                        Open
                      </span>
                    </div>
                    <h4 className="font-semibold text-white">{resource.title}</h4>
                    <p className="text-sm text-slate-400">{resource.description}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseWiki;
