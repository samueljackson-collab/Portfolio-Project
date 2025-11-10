import {
  Activity,
  Book,
  CheckCircle,
  ChevronRight,
  Code,
  FileText,
  GitBranch,
  Network,
  Server,
  Shield,
  TestTube,
} from 'lucide-react';
import type {
  RoleDefinition,
  RoleKey,
  RoleTheme,
} from './enterpriseWikiTypes';
import { roleContent } from './__private__/enterpriseWikiContent';

// The exported metadata keeps the component tidy. Deep-dive curriculum text lives
// in __private__/enterpriseWikiContent.ts so the presentation layer only pulls in
// what it needs at render time.
export const roles: Record<RoleKey, RoleDefinition> = {
  sde: {
    title: 'System Development Engineer',
    icon: Server,
    description: 'Infrastructure, automation, and system reliability',
    weeks: 8,
  },
  devops: {
    title: 'DevOps Engineer',
    icon: GitBranch,
    description: 'CI/CD, GitOps, and deployment automation',
    weeks: 6,
  },
  qa: {
    title: 'QA Engineer III',
    icon: TestTube,
    description: 'Testing strategy, automation, and quality assurance',
    weeks: 6,
  },
  architect: {
    title: 'Solutions Architect',
    icon: Network,
    description: 'System design, architecture patterns, and trade-offs',
    weeks: 8,
  },
};

export const roleThemes: Record<RoleKey, RoleTheme> = {
  sde: {
    accentBg: 'bg-blue-600',
    accentHoverBg: 'hover:bg-blue-700',
    selectedButton: 'bg-blue-600 text-white shadow-lg scale-105',
  },
  devops: {
    accentBg: 'bg-green-600',
    accentHoverBg: 'hover:bg-green-700',
    selectedButton: 'bg-green-600 text-white shadow-lg scale-105',
  },
  qa: {
    accentBg: 'bg-purple-600',
    accentHoverBg: 'hover:bg-purple-700',
    selectedButton: 'bg-purple-600 text-white shadow-lg scale-105',
  },
  architect: {
    accentBg: 'bg-orange-600',
    accentHoverBg: 'hover:bg-orange-700',
    selectedButton: 'bg-orange-600 text-white shadow-lg scale-105',
  },
};

export const enterpriseWikiIcons = {
  Activity,
  Book,
  CheckCircle,
  ChevronRight,
  Code,
  FileText,
  Shield,
} as const;

export { roleContent };
export * from './enterpriseWikiTypes';
