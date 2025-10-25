import type { LucideIcon } from 'lucide-react';

// Shared type definitions keep the UI, metadata, and private curriculum in sync.
export type RoleKey = 'sde' | 'devops' | 'qa' | 'architect';

export type RoleDefinition = {
  title: string;
  icon: LucideIcon;
  description: string;
  weeks: number;
};

export type RoleTheme = {
  accentBg: string;
  accentHoverBg: string;
  selectedButton: string;
};

export type WeekPlan = {
  number: number;
  title: string;
  topics: string[];
  deliverables: string[];
};

export type RoleContent = {
  overview: {
    responsibilities: string[];
    skills: string[];
  };
  weeks: WeekPlan[];
};
