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
  PhotoListResponse,
  PhotoUploadResponse,
  CalendarMonthResponse,
  Album,
  AlbumListResponse,
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

export const albumService = {
  async list(): Promise<Album[]> {
    const response = await apiClient.get<AlbumListResponse>('/photos/albums')
    return response.data.items
  },
}

export const photoService = {
  async list(params?: { skip?: number; limit?: number; albumId?: string }): Promise<PhotoListResponse> {
    const response = await apiClient.get<PhotoListResponse>('/photos', {
      params: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 50,
        album_id: params?.albumId,
      },
    })
    return response.data
  },

  async upload(file: File): Promise<PhotoUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<PhotoUploadResponse>('/photos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async fetchPhotoBlob(id: string, options?: { thumbnail?: boolean }): Promise<Blob> {
    const response = await apiClient.get<Blob>(`/photos/${id}/file`, {
      params: { thumbnail: options?.thumbnail ?? false },
      responseType: 'blob',
    })
    return response.data
  },

  async getCalendar(year: number, month: number): Promise<CalendarMonthResponse> {
    const response = await apiClient.get<CalendarMonthResponse>('/photos/calendar', {
      params: { year, month },
    })
    return response.data
  },
}
