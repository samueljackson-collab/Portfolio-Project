/**
 * Comprehensive tests for API client
 * 
 * Tests cover:
 * - Request interceptors
 * - Response interceptors
 * - Error handling
 * - Token injection
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import apiClient from './client'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: {
          use: vi.fn(),
        },
        response: {
          use: vi.fn(),
        },
      },
    })),
  },
}))

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should create axios instance with correct config', () => {
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: expect.any(String),
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    })
  })

  it('should have request interceptor registered', () => {
    expect(apiClient.interceptors.request.use).toHaveBeenCalled()
  })

  it('should have response interceptor registered', () => {
    expect(apiClient.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('Request Interceptor', () => {
  it('should add authorization header when token exists', () => {
    localStorage.getItem = vi.fn(() => 'test_token')
    
    const config: any = {
      headers: {},
    }

    // Get the request interceptor function
    const requestInterceptor = vi.mocked(apiClient.interceptors.request.use).mock.calls[0][0]
    const modifiedConfig = requestInterceptor(config)

    expect(modifiedConfig.headers.Authorization).toBe('Bearer test_token')
  })

  it('should not add authorization header when token does not exist', () => {
    localStorage.getItem = vi.fn(() => null)
    
    const config: any = {
      headers: {},
    }

    const requestInterceptor = vi.mocked(apiClient.interceptors.request.use).mock.calls[0][0]
    const modifiedConfig = requestInterceptor(config)

    expect(modifiedConfig.headers.Authorization).toBeUndefined()
  })
})

describe('Response Interceptor', () => {
  beforeEach(() => {
    // Reset window.location mock
    delete (window as any).location
    window.location = {
      href: '',
      pathname: '/',
      assign: vi.fn(),
      replace: vi.fn(),
      reload: vi.fn(),
    } as any
  })

  it('should return response on success', () => {
    const response = { data: { message: 'success' } }
    
    const responseInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][0]
    const result = responseInterceptor(response)

    expect(result).toEqual(response)
  })

  it('should handle 401 errors by clearing storage and redirecting', () => {
    const error: any = {
      response: {
        status: 401,
        data: { detail: 'Unauthorized' },
      },
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    expect(window.location.href).toBe('/login')
  })

  it('should log 403 errors', () => {
    const error: any = {
      response: {
        status: 403,
        data: { detail: 'Forbidden' },
      },
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('Access forbidden:', error.response.data)
  })

  it('should log 404 errors', () => {
    const error: any = {
      response: {
        status: 404,
        data: { detail: 'Not found' },
      },
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('Resource not found:', error.response.data)
  })

  it('should log 422 validation errors', () => {
    const error: any = {
      response: {
        status: 422,
        data: { detail: [{ msg: 'Invalid field' }] },
      },
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('Validation error:', error.response.data)
  })

  it('should log 500 server errors', () => {
    const error: any = {
      response: {
        status: 500,
        data: { detail: 'Internal server error' },
      },
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('Server error:', error.response.data)
  })

  it('should handle request errors (no response)', () => {
    const error: any = {
      request: {},
      message: 'Network error',
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('No response received:', error.request)
  })

  it('should handle setup errors', () => {
    const error: any = {
      message: 'Request setup error',
    }

    const errorInterceptor = vi.mocked(apiClient.interceptors.response.use).mock.calls[0][1]
    
    expect(() => errorInterceptor(error)).rejects.toEqual(error)
    expect(console.error).toHaveBeenCalledWith('Request error:', error.message)
  })
})