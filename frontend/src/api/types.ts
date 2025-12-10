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

// Photo and Album Types

export interface Photo {
  id: string
  owner_id: string
  album_id: string | null
  filename: string
  file_path: string
  thumbnail_path: string | null
  file_size: number
  mime_type: string
  width: number | null
  height: number | null
  capture_date: string | null
  upload_date: string
  latitude: number | null
  longitude: number | null
  city: string | null
  state: string | null
  country: string | null
  camera_make: string | null
  camera_model: string | null
  created_at: string
  updated_at: string
}

export interface Album {
  id: string
  owner_id: string
  name: string
  type: 'location' | 'date' | 'custom'
  photo_count: number
  cover_photo_id: string | null
  created_at: string
  updated_at: string
}

export interface PhotoListResponse {
  items: Photo[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface AlbumListResponse {
  items: Album[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface PhotoUploadResponse {
  photo: Photo
  album: Album | null
  message: string
}

export interface CalendarDateResponse {
  date: string
  photo_count: number
  preview_photos: Photo[]
}

export interface CalendarMonthResponse {
  year: number
  month: number
  dates: CalendarDateResponse[]
  total_photos: number
}

export interface OrchestrationPlan {
  id: string
  name: string
  environment: string
  description: string
  playbook_path: string
  tfvars_file: string
  runbook: string
}

export interface OrchestrationRunRequest {
  plan_id: string
  parameters?: Record<string, string>
}

export interface OrchestrationRun {
  id: string
  plan_id: string
  environment: string
  status: 'running' | 'succeeded' | 'failed'
  requested_by: string
  parameters: Record<string, string>
  started_at: string
  finished_at: string | null
  logs: string[]
  artifacts: Record<string, string>
  summary?: string
}
