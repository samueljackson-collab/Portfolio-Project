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

// Deployment / operations types
export interface DeploymentRecord {
  id: string
  service_name: string
  region: string
  cluster: string
  version: string
  status: string
  git_commit?: string
  desired_replicas: number
  available_replicas: number
  created_at: string
  updated_at: string
}

export interface RegionRollup {
  region: string
  services: number
  desired_replicas: number
  available_replicas: number
  healthy: number
}

export interface DeploymentDashboardResponse {
  regions: RegionRollup[]
  latest_releases: DeploymentRecord[]
}
