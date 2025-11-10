/**
 * Axios API Client
 *
 * Configured Axios instance with interceptors for:
 * - Authentication token injection
 * - Error handling
 * - Request/response logging
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { ApiError } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

/**
 * Create Axios instance with base configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

/**
 * Request interceptor to add authentication token
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // Handle specific error status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break

        case 403:
          // Forbidden
          console.error('Access forbidden:', error.response.data)
          break

        case 404:
          // Not found
          console.error('Resource not found:', error.response.data)
          break

        case 422:
          // Validation error
          console.error('Validation error:', error.response.data)
          break

        case 500:
          // Server error
          console.error('Server error:', error.response.data)
          break

        default:
          console.error('API error:', error.response.data)
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response received:', error.request)
    } else {
      // Error in request setup
      console.error('Request error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
