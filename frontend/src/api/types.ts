export interface User {
  id: number
  email: string
  username: string
  is_admin: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface Project {
  id: number
  title: string
  slug: string
  description: string
  category: string
  tags: string[]
  repo_url?: string | null
  live_url?: string | null
  featured: boolean
  created_at: string
  updated_at: string
}

export interface ProjectPayload {
  title: string
  slug: string
  description: string
  category: string
  tags: string[]
  repo_url?: string | null
  live_url?: string | null
  featured?: boolean
}

export interface ApiError {
  detail: string | Record<string, unknown>[]
}
