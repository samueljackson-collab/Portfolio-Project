import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
});

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ProjectPayload {
  title: string;
  description?: string;
}

export interface Project extends ProjectPayload {
  id: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(
    '/auth/token',
    new URLSearchParams({ username, password })
  );
  return response.data;
}

export async function listProjects(token: string): Promise<Project[]> {
  const response = await api.get<Project[]>('/projects', {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
}

export async function createProject(token: string, payload: ProjectPayload): Promise<Project> {
  const response = await api.post<Project>('/projects', payload, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
}
