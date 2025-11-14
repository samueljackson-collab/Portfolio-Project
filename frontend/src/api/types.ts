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

export interface Album {
  id: string
  owner_id: string
  name: string
  description?: string | null
  type: string
  cover_photo_id?: string | null
  photo_count: number
  created_at: string
  updated_at: string
}

export interface Photo {
  id: string
  owner_id: string
  album_id?: string | null
  title?: string | null
  description?: string | null
  file_name: string
  mime_type: string
  file_size: number
  width?: number | null
  height?: number | null
  capture_date?: string | null
  camera_make?: string | null
  camera_model?: string | null
  focal_length?: string | null
  aperture?: string | null
  iso?: number | null
  latitude?: number | null
  longitude?: number | null
  location_name?: string | null
  city?: string | null
  state?: string | null
  country?: string | null
  file_url?: string | null
  thumbnail_url?: string | null
  created_at: string
  updated_at: string
}

export interface PhotoListResponse {
  items: Photo[]
  total: number
}

export interface PhotoUploadResponse extends Photo {
  message: string
}

export interface CalendarDateResponse {
  date: string
  photo_count: number
  preview_photos: Photo[]
}

export interface CalendarMonthResponse {
  total_photos: number
  dates: CalendarDateResponse[]
}

export interface AlbumListResponse {
  items: Album[]
}
