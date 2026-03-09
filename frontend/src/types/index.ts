/**
 * Frontend Type Definitions
 */

export interface Project {
  id: string;
  name: string;
  description: string;
  technologies: string[];
  status?: 'active' | 'completed' | 'planned';
  url?: string;
}
