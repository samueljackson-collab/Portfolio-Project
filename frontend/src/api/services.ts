/**
 * API Services
 *
 * Service functions for interacting with the backend API
 */

import apiClient from './client'
import type {
  User,
  Content,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  CreateContentRequest,
  UpdateContentRequest,
  Photo,
  Album,
  PhotoListResponse,
  AlbumListResponse,
  PhotoUploadResponse,
  CalendarMonthResponse,
} from './types'

/**
 * Authentication Services
 */
export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },

  /**
   * Login user and get access token
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },
}

/**
 * Content Services
 */
export const contentService = {
  /**
   * Get all content items with optional pagination
   */
  async getAll(skip = 0, limit = 100): Promise<Content[]> {
    const response = await apiClient.get<Content[]>('/content', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Get a single content item by ID
   */
  async getById(id: string): Promise<Content> {
    const response = await apiClient.get<Content>(`/content/${id}`)
    return response.data
  },

  /**
   * Create a new content item
   */
  async create(data: CreateContentRequest): Promise<Content> {
    const response = await apiClient.post<Content>('/content', data)
    return response.data
  },

  /**
   * Update an existing content item
   */
  async update(id: string, data: UpdateContentRequest): Promise<Content> {
    const response = await apiClient.put<Content>(`/content/${id}`, data)
    return response.data
  },

  /**
   * Delete a content item
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/content/${id}`)
  },
}

/**
 * Health Check Service
 */
export const healthService = {
  /**
   * Check API health status
   */
  async check(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get<{ status: string; timestamp: string }>('/health')
    return response.data
  },
}

/**
 * Photo Services
 */
export const photoService = {
  /**
   * Upload a photo file
   */
  async upload(file: File): Promise<PhotoUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<PhotoUploadResponse>('/photos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Get all photos with optional filtering and pagination
   */
  async getAll(params?: {
    page?: number
    page_size?: number
    album_id?: string
    city?: string
    year?: number
    month?: number
  }): Promise<PhotoListResponse> {
    const response = await apiClient.get<PhotoListResponse>('/photos', { params })
    return response.data
  },

  /**
   * Get a single photo by ID
   */
  async getById(id: string): Promise<Photo> {
    const response = await apiClient.get<Photo>(`/photos/${id}`)
    return response.data
  },

  /**
   * Get photo file URL (for displaying image)
   */
  getFileUrl(id: string, thumbnail = false): string {
    const baseUrl = apiClient.defaults.baseURL || ''
    return `${baseUrl}/photos/${id}/file${thumbnail ? '?thumbnail=true' : ''}`
  },

  /**
   * Delete a photo
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/photos/${id}`)
  },

  /**
   * Get calendar view for a specific month
   */
  async getCalendarMonth(year: number, month: number): Promise<CalendarMonthResponse> {
    const response = await apiClient.get<CalendarMonthResponse>(
      `/photos/calendar/${year}/${month}`
    )
    return response.data
  },
}

/**
 * Album Services
 */
export const albumService = {
  /**
   * Get all albums with optional filtering and pagination
   */
  async getAll(params?: {
    page?: number
    page_size?: number
    album_type?: 'location' | 'date' | 'custom'
  }): Promise<AlbumListResponse> {
    const response = await apiClient.get<AlbumListResponse>('/photos/albums', { params })
    return response.data
  },
}
