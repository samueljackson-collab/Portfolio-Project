/**
 * Comprehensive tests for API services
 * 
 * Tests cover:
 * - Authentication service methods
 * - Content service methods
 * - Health check service
 * - Error handling
 * - Edge cases
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { authService, contentService, healthService } from './services'
import apiClient from './client'

// Mock the API client
vi.mock('./client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('register', () => {
    it('should register a new user', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockUser })

      const result = await authService.register({
        email: 'test@example.com',
        password: 'SecurePass123',
      })

      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', {
        email: 'test@example.com',
        password: 'SecurePass123',
      })
      expect(result).toEqual(mockUser)
    })

    it('should handle registration errors', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Registration failed'))

      await expect(
        authService.register({
          email: 'test@example.com',
          password: 'SecurePass123',
        })
      ).rejects.toThrow('Registration failed')
    })
  })

  describe('login', () => {
    it('should login user and return token', async () => {
      const mockResponse = {
        access_token: 'mock_token',
        token_type: 'bearer',
        expires_in: 1800,
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await authService.login({
        username: 'test@example.com',
        password: 'password123',
      })

      expect(apiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle login errors', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Invalid credentials'))

      await expect(
        authService.login({
          username: 'test@example.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials')
    })
  })

  describe('getCurrentUser', () => {
    it('should fetch current user data', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockUser })

      const result = await authService.getCurrentUser()

      expect(apiClient.get).toHaveBeenCalledWith('/auth/me')
      expect(result).toEqual(mockUser)
    })

    it('should handle unauthorized errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Unauthorized'))

      await expect(authService.getCurrentUser()).rejects.toThrow('Unauthorized')
    })
  })
})

describe('contentService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAll', () => {
    it('should fetch all content items', async () => {
      const mockContent = [
        {
          id: '1',
          title: 'Test Content',
          body: 'Test body',
          is_published: true,
          owner_id: '123',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockContent })

      const result = await contentService.getAll()

      expect(apiClient.get).toHaveBeenCalledWith('/content', {
        params: { skip: 0, limit: 100 },
      })
      expect(result).toEqual(mockContent)
    })

    it('should fetch content with custom pagination', async () => {
      const mockContent = []
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockContent })

      await contentService.getAll(10, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/content', {
        params: { skip: 10, limit: 20 },
      })
    })

    it('should handle fetch errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Fetch failed'))

      await expect(contentService.getAll()).rejects.toThrow('Fetch failed')
    })
  })

  describe('getById', () => {
    it('should fetch content by ID', async () => {
      const mockContent = {
        id: '1',
        title: 'Test Content',
        body: 'Test body',
        is_published: true,
        owner_id: '123',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockContent })

      const result = await contentService.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/content/1')
      expect(result).toEqual(mockContent)
    })

    it('should handle not found errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Not found'))

      await expect(contentService.getById('999')).rejects.toThrow('Not found')
    })
  })

  describe('create', () => {
    it('should create new content', async () => {
      const newContent = {
        title: 'New Content',
        body: 'New body',
        is_published: false,
      }

      const mockResponse = {
        id: '1',
        ...newContent,
        owner_id: '123',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await contentService.create(newContent)

      expect(apiClient.post).toHaveBeenCalledWith('/content', newContent)
      expect(result).toEqual(mockResponse)
    })

    it('should handle creation errors', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Creation failed'))

      await expect(
        contentService.create({
          title: 'Test',
          body: 'Body',
          is_published: false,
        })
      ).rejects.toThrow('Creation failed')
    })
  })

  describe('update', () => {
    it('should update existing content', async () => {
      const updates = {
        title: 'Updated Title',
        is_published: true,
      }

      const mockResponse = {
        id: '1',
        title: 'Updated Title',
        body: 'Original body',
        is_published: true,
        owner_id: '123',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T12:00:00Z',
      }

      vi.mocked(apiClient.put).mockResolvedValue({ data: mockResponse })

      const result = await contentService.update('1', updates)

      expect(apiClient.put).toHaveBeenCalledWith('/content/1', updates)
      expect(result).toEqual(mockResponse)
    })

    it('should handle update errors', async () => {
      vi.mocked(apiClient.put).mockRejectedValue(new Error('Update failed'))

      await expect(
        contentService.update('1', { title: 'Updated' })
      ).rejects.toThrow('Update failed')
    })
  })

  describe('delete', () => {
    it('should delete content', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null })

      await contentService.delete('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/content/1')
    })

    it('should handle delete errors', async () => {
      vi.mocked(apiClient.delete).mockRejectedValue(new Error('Delete failed'))

      await expect(contentService.delete('1')).rejects.toThrow('Delete failed')
    })
  })
})

describe('healthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('check', () => {
    it('should check API health', async () => {
      const mockHealth = {
        status: 'healthy',
        timestamp: '2024-01-01T00:00:00Z',
      }

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockHealth })

      const result = await healthService.check()

      expect(apiClient.get).toHaveBeenCalledWith('/health')
      expect(result).toEqual(mockHealth)
    })

    it('should handle health check errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Service unavailable'))

      await expect(healthService.check()).rejects.toThrow('Service unavailable')
    })
  })
})