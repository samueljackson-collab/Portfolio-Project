import React, { useMemo, useState } from 'react';
import {
  enterpriseWikiIcons,
  roleContent,
  roleThemes,
  roles,
} from './enterpriseWikiData';
import type {
  RoleDefinition,
  RoleKey,
  RoleTheme,
  WeekPlan,
} from './enterpriseWikiData';

const { Book, CheckCircle, ChevronRight, Code, FileText, Shield, Activity } =
  enterpriseWikiIcons;

const wikiPageUrl =
  'https://github.com/samueljackson-collab/Portfolio-Project/blob/main/docs/enterprise-wiki/README.md';

const createWikiLink = (anchor: string) => `${wikiPageUrl}#${anchor}`;

// Lightweight helper to assemble Tailwind class strings without pulling in a
// third-party dependency just for conditional styling.
const classNames = (
  ...classes: Array<string | false | null | undefined>
): string => classes.filter(Boolean).join(' ');

// WeekDetail keeps the weekly curriculum rendering focused and predictable.
const WeekDetail: React.FC<{
  week: WeekPlan;
  theme: RoleTheme;
  guideAnchorId: string;
  resourcesAnchorId: string;
  roleTitle: string;
  wikiGuideHref: string;
  wikiResourcesHref: string;
}> = ({
  week,
  theme,
  guideAnchorId,
  resourcesAnchorId,
  roleTitle,
  wikiGuideHref,
  wikiResourcesHref,
}) => (
  <div
    className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-2xl"
    id={guideAnchorId}
  >
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

    <div
      className="mt-6 pt-6 border-t border-white/10 flex gap-4"
      id={resourcesAnchorId}
    >
      <a
        href={wikiGuideHref}
        className={classNames(
          'flex-1 py-3 px-6 text-white rounded-lg font-semibold transition-colors text-center',
          theme.accentBg,
          theme.accentHoverBg,
        )}
        target="_blank"
        rel="noreferrer"
        aria-label={`View the detailed guide for ${roleTitle} week ${week.number}: ${week.title}`}
      >
        View Detailed Guide
      </a>
      <a
        href={wikiResourcesHref}
        className="py-3 px-6 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition-colors text-center"
        target="_blank"
        rel="noreferrer"
        aria-label={`Open the resource collection for ${roleTitle} week ${week.number}: ${week.title}`}
      >
        Access Resources
      </a>
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

  const createWeekSlug = (value: string) =>
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)+/g, '');

  const weekSlug = useMemo(
    () => createWeekSlug(`week-${activeWeek.number}-${activeWeek.title}`),
    [activeWeek.number, activeWeek.title],
  );

  const createAnchorId = (suffix: string) => `${weekSlug}-${suffix}`;

  const guideAnchorId = createAnchorId('guide');
  const resourcesAnchorId = createAnchorId('resources');
  const codeExamplesAnchorId = createAnchorId('code-examples');
  const liveDemosAnchorId = createAnchorId('live-demos');
  const bestPracticesAnchorId = createAnchorId('best-practices');
  const wikiGuideHref = createWikiLink(guideAnchorId);
  const wikiResourcesHref = createWikiLink(resourcesAnchorId);
  const codeExamplesHref = createWikiLink(codeExamplesAnchorId);
  const liveDemosHref = createWikiLink(liveDemosAnchorId);
  const bestPracticesHref = createWikiLink(bestPracticesAnchorId);

  // Protect against rounding overshooting 100% when the last week is active.
  const progressPercentage = useMemo(
    () => Math.min(100, Math.round((selectedWeek / currentRole.weeks) * 100)),
    [selectedWeek, currentRole.weeks],
  );

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-10 top-0 h-64 w-64 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute right-16 top-12 h-72 w-72 rounded-full bg-purple-500/20 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.05),transparent_35%)]" />
      </div>

      <div className="relative container mx-auto px-4 py-10 lg:py-16">
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/30 via-transparent to-purple-600/30" />
          <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-100">
                Enterprise learning paths
              </div>
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 shadow-lg shadow-blue-900/30">
                  <Book className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold text-white">
                    Enterprise Portfolio Wiki
                  </h1>
                  <p className="text-blue-50/90">
                    Browse role-based week-by-week guides with deep links to the wiki reference.
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-3">
                <a
                  href={wikiPageUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-400 via-blue-500 to-purple-500 px-5 py-2.5 text-sm font-semibold text-slate-950 shadow-lg shadow-blue-500/40 transition hover:translate-y-[-2px]"
                >
                  Open wiki reference
                </a>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-slate-100">
                  Auto-updated anchors per week
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-blue-50">
                <p className="text-xs uppercase tracking-[0.2em] text-blue-100/70">Roles</p>
                <p className="text-3xl font-semibold">4</p>
                <p className="text-xs text-blue-50/70">SDE, DevOps, QA, Architect</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-blue-50">
                <p className="text-xs uppercase tracking-[0.2em] text-blue-100/70">Weeks mapped</p>
                <p className="text-3xl font-semibold">28</p>
                <p className="text-xs text-blue-50/70">Deep-linked to wiki anchors</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6 mt-8">
          <div className="lg:col-span-1">
            <div className="sticky top-6 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-xl">
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
                        'w-full rounded-xl border border-white/10 p-4 text-left transition-all backdrop-blur',
                        isSelected
                          ? roleThemes[key].selectedButton
                          : 'bg-white/5 text-slate-200 hover:bg-white/10',
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

              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-sm font-semibold text-slate-200 mb-3">Your Progress</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-slate-300">
                    <span>
                      Week {selectedWeek} of {currentRole.weeks}
                    </span>
                    <span>{progressPercentage}%</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
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

          <div className="lg:col-span-3 space-y-6">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-xl">
              <div className="flex items-center gap-4 mb-4">
                <div
                  className={classNames(
                    'p-3 rounded-xl shadow-lg shadow-blue-900/30',
                    currentTheme.accentBg,
                  )}
                >
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

            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Learning Path Timeline</h3>
                <span className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold text-slate-100">
                  Jump to any week
                </span>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {currentContent.weeks.map((week) => {
                  const isActiveWeek = selectedWeek === week.number;
                  return (
                    <button
                      key={week.number}
                      onClick={() => setSelectedWeek(week.number)}
                      className={classNames(
                        'px-4 py-2 rounded-lg whitespace-nowrap transition-all border border-white/10 backdrop-blur',
                        isActiveWeek
                          ? classNames(currentTheme.accentBg, 'text-white shadow-lg shadow-blue-900/30')
                          : 'bg-white/5 text-slate-200 hover:bg-white/10',
                      )}
                    >
                      Week {week.number}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Always render at least one week so the layout stays consistent. */}
            {activeWeek && (
              <WeekDetail
                week={activeWeek}
                theme={currentTheme}
                guideAnchorId={guideAnchorId}
                resourcesAnchorId={resourcesAnchorId}
                roleTitle={currentRole.title}
                wikiGuideHref={wikiGuideHref}
                wikiResourcesHref={wikiResourcesHref}
              />
            )}

            <div className="grid md:grid-cols-3 gap-4 mt-6">
              <a
                href={codeExamplesHref}
                id={codeExamplesAnchorId}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 hover:border-white/30 hover:bg-white/10 transition-colors cursor-pointer block backdrop-blur-xl"
                target="_blank"
                rel="noreferrer"
                aria-label={`Browse code examples for ${currentRole.title} week ${activeWeek.number}`}
              >
                <Code className="w-8 h-8 text-blue-500 mb-2" />
                <h4 className="font-semibold text-white">Code Examples</h4>
                <p className="text-sm text-slate-400">Full implementation samples</p>
              </a>
              <a
                href={liveDemosHref}
                id={liveDemosAnchorId}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 hover:border-white/30 hover:bg-white/10 transition-colors cursor-pointer block backdrop-blur-xl"
                target="_blank"
                rel="noreferrer"
                aria-label={`Open live demos for ${currentRole.title} week ${activeWeek.number}`}
              >
                <Activity className="w-8 h-8 text-green-500 mb-2" />
                <h4 className="font-semibold text-white">Live Demos</h4>
                <p className="text-sm text-slate-400">Interactive tutorials</p>
              </a>
              <a
                href={bestPracticesHref}
                id={bestPracticesAnchorId}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 hover:border-white/30 hover:bg-white/10 transition-colors cursor-pointer block backdrop-blur-xl"
                target="_blank"
                rel="noreferrer"
                aria-label={`Review best practices for ${currentRole.title} week ${activeWeek.number}`}
              >
                <Shield className="w-8 h-8 text-purple-500 mb-2" />
                <h4 className="font-semibold text-white">Best Practices</h4>
                <p className="text-sm text-slate-400">Industry standards</p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseWiki;
