import apiClient from './client'
import type {
  ApiError,
  LoginRequest,
  LoginResponse,
  Project,
  ProjectPayload,
  RegisterRequest,
  User,
} from './types'

export const authService = {
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },
}

export const projectService = {
  async list(): Promise<Project[]> {
    const response = await apiClient.get<Project[]>('/projects/')
    return response.data
  },
  async get(slug: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${slug}`)
    return response.data
  },
  async create(payload: ProjectPayload): Promise<Project> {
    const response = await apiClient.post<Project>('/projects/', payload)
    return response.data
  },
  async update(slug: string, payload: Partial<ProjectPayload>): Promise<Project> {
    const response = await apiClient.put<Project>(`/projects/${slug}`, payload)
    return response.data
  },
  async remove(slug: string): Promise<void> {
    await apiClient.delete(`/projects/${slug}`)
  },
}

export type { ApiError, User, Project }
