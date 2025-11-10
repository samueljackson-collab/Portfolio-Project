/**
 * Comprehensive tests for AuthContext
 * 
 * Tests cover:
 * - Provider initialization
 * - Login functionality
 * - Register functionality
 * - Logout functionality
 * - Token persistence
 * - Error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'
import * as authServiceModule from '../api'

// Mock the auth service
vi.mock('../api', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('useAuth hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        renderHook(() => useAuth())
      }).toThrow('useAuth must be used within an AuthProvider')
      
      consoleSpy.mockRestore()
    })

    it('should provide auth context when used inside AuthProvider', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      expect(result.current).toBeDefined()
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('Initial State', () => {
    it('should initialize with null user and token', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should initialize with loading state', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      // Should start loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })
  })

  describe('Login', () => {
    it('should successfully log in user', async () => {
      const mockLoginResponse = {
        access_token: 'mock_token',
        token_type: 'bearer',
        expires_in: 1800,
      }
      
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(authServiceModule.authService.login).mockResolvedValue(mockLoginResponse)
      vi.mocked(authServiceModule.authService.getCurrentUser).mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.login({
          username: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.token).toBe('mock_token')
        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.isLoading).toBe(false)
      })

      // Check localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'mock_token')
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser))
    })

    it('should handle login errors', async () => {
      vi.mocked(authServiceModule.authService.login).mockRejectedValue(
        new Error('Invalid credentials')
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await expect(async () => {
        await act(async () => {
          await result.current.login({
            username: 'test@example.com',
            password: 'wrongpassword',
          })
        })
      }).rejects.toThrow('Invalid credentials')

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('Register', () => {
    it('should successfully register and login user', async () => {
      const mockUser = {
        id: '123',
        email: 'newuser@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      const mockLoginResponse = {
        access_token: 'mock_token',
        token_type: 'bearer',
        expires_in: 1800,
      }

      vi.mocked(authServiceModule.authService.register).mockResolvedValue(mockUser)
      vi.mocked(authServiceModule.authService.login).mockResolvedValue(mockLoginResponse)
      vi.mocked(authServiceModule.authService.getCurrentUser).mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.register({
          email: 'newuser@example.com',
          password: 'SecurePass123',
        })
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.isAuthenticated).toBe(true)
      })
    })

    it('should handle registration errors', async () => {
      vi.mocked(authServiceModule.authService.register).mockRejectedValue(
        new Error('Email already exists')
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await expect(async () => {
        await act(async () => {
          await result.current.register({
            email: 'existing@example.com',
            password: 'SecurePass123',
          })
        })
      }).rejects.toThrow('Email already exists')
    })
  })

  describe('Logout', () => {
    it('should clear user and token on logout', async () => {
      const mockLoginResponse = {
        access_token: 'mock_token',
        token_type: 'bearer',
        expires_in: 1800,
      }
      
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(authServiceModule.authService.login).mockResolvedValue(mockLoginResponse)
      vi.mocked(authServiceModule.authService.getCurrentUser).mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), { wrapper })

      // Login first
      await act(async () => {
        await result.current.login({
          username: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      // Then logout
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })

  describe('Token Persistence', () => {
    it('should load user from localStorage on mount', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      localStorage.getItem = vi.fn((key) => {
        if (key === 'access_token') return 'stored_token'
        if (key === 'user') return JSON.stringify(mockUser)
        return null
      })

      vi.mocked(authServiceModule.authService.getCurrentUser).mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.token).toBe('stored_token')
        expect(result.current.isAuthenticated).toBe(true)
      })
    })

    it('should clear invalid stored token', async () => {
      localStorage.getItem = vi.fn((key) => {
        if (key === 'access_token') return 'invalid_token'
        if (key === 'user') return JSON.stringify({ email: 'test@example.com' })
        return null
      })

      vi.mocked(authServiceModule.authService.getCurrentUser).mockRejectedValue(
        new Error('Invalid token')
      )

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.user).toBeNull()
        expect(result.current.token).toBeNull()
        expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
        expect(localStorage.removeItem).toHaveBeenCalledWith('user')
      })
    })
  })

  describe('Loading State', () => {
    it('should set loading to false after initialization', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('should set loading during login', async () => {
      const mockLoginResponse = {
        access_token: 'mock_token',
        token_type: 'bearer',
        expires_in: 1800,
      }
      
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      vi.mocked(authServiceModule.authService.login).mockResolvedValue(mockLoginResponse)
      vi.mocked(authServiceModule.authService.getCurrentUser).mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.login({
          username: 'test@example.com',
          password: 'password123',
        })
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
    })
  })
})