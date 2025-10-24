import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface Project {
  id: string;
  name: string;
  description: string;
  tags: string[];
  url: string;
}

export interface HealthResponse {
  status: string;
  environment: string;
}

export async function fetchProjects(): Promise<Project[]> {
  const response = await axios.get<Project[]>(`${BASE_URL}/api/projects`);
  return response.data;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await axios.get<HealthResponse>(`${BASE_URL}/health`);
  return response.data;
}
