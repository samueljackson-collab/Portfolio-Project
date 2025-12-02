/**
 * API Type Definitions
 *
 * TypeScript interfaces for API requests and responses
 */

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Content {
  id: string
  title: string
  body: string | null
  owner_id: string
  is_published: boolean
  created_at: string
  updated_at: string
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
  password: string
}

export interface CreateContentRequest {
  title: string
  body?: string
  is_published?: boolean
}

export interface UpdateContentRequest {
  title?: string
  body?: string
  is_published?: boolean
}

export interface ApiError {
  detail: string | Record<string, unknown>[]
}
