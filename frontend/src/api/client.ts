/**
 * Axios API Client
 *
 * A pre-configured Axios instance that all service functions in services.ts use.
 * It handles two cross-cutting concerns automatically via interceptors:
 *
 * 1. REQUEST INTERCEPTOR — injects the JWT from localStorage as an
 *    Authorization: Bearer <token> header on every outgoing request.
 *    This means individual service functions never need to touch localStorage.
 *
 * 2. RESPONSE INTERCEPTOR — catches HTTP error responses and:
 *    - On 401: clears auth storage and redirects to /login (see note below)
 *    - On other errors: logs the error and re-throws so the caller can handle it
 *
 * BASE URL:
 *   In development (npm run dev), Vite proxies /api/* to http://localhost:8000
 *   via the proxy config in vite.config.ts, so VITE_API_URL defaults to '/api'.
 *   In production, set VITE_API_URL in your environment to the full API URL.
 *
 * TIMEOUT:
 *   10 seconds — long enough for slow backend cold starts in demo environments,
 *   short enough to give users prompt feedback if the server is unreachable.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { ApiError } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

/**
 * Shared Axios instance — import this in services.ts instead of calling
 * axios.create() each time, so all requests share the same configuration
 * and interceptors.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds — see module comment above
})

/**
 * Request interceptor — attach the JWT to every outgoing request.
 *
 * WHY READ FROM localStorage HERE (not from React state)?
 * This interceptor runs outside the React component tree, so it cannot access
 * the AuthContext. Reading from localStorage is the standard pattern for
 * Axios interceptors — it works because AuthContext writes to localStorage
 * whenever the token changes (see AuthContext.tsx login/logout functions).
 *
 * The token is read fresh on each request (not cached in a closure) so that
 * token changes (e.g. after login) are picked up immediately without
 * re-creating the Axios instance.
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
 * Response interceptor — global error handling for all API responses.
 *
 * Successful responses (2xx) pass through unchanged.
 *
 * For errors, we switch on the HTTP status code:
 *
 * 401 UNAUTHORIZED:
 *   The JWT has expired or was rejected by the server. We clear auth storage
 *   and redirect to /login.
 *
 *   WHY window.location INSTEAD OF React Router navigate():
 *   This interceptor is module-level code — it runs outside the React tree
 *   and has no access to the Router context. window.location.href is the
 *   correct tool here. The full-page navigation also clears all in-memory
 *   React state, which is the behaviour we want on logout.
 *
 *   WHY THE pathname CHECK:
 *   Without it, a failed login attempt (which returns 401) would redirect
 *   back to /login, creating an infinite loop. The guard ensures we only
 *   redirect when the user is on a non-login page.
 *
 * 403 FORBIDDEN:
 *   The token is valid but the user lacks permission for this resource.
 *   Logged and re-thrown — the calling component handles the UX.
 *
 * 404 NOT FOUND / 422 VALIDATION ERROR / 500 SERVER ERROR:
 *   Logged for debugging and re-thrown. The calling service or component
 *   is responsible for displaying user-friendly error messages.
 */
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          // Guard against redirect loops from the login page itself
          if (!window.location.pathname.startsWith('/login')) {
            window.location.href = '/login'
          }
          break

        case 403:
          console.error('Access forbidden:', error.response.data)
          break

        case 404:
          console.error('Resource not found:', error.response.data)
          break

        case 422:
          // FastAPI returns 422 for request body validation failures.
          // The detail field contains an array of field-level error messages.
          console.error('Validation error:', error.response.data)
          break

        case 500:
          console.error('Server error:', error.response.data)
          break

        default:
          console.error('API error:', error.response.data)
      }
    } else if (error.request) {
      // The request was made but no response was received — likely a network
      // error (server down, CORS preflight blocked, DNS failure).
      console.error('No response received:', error.request)
    } else {
      // Something went wrong building the request itself (e.g. bad config)
      console.error('Request error:', error.message)
    }

    // Always re-throw so the calling service/component can catch and handle
    // the error with appropriate user-facing feedback.
    return Promise.reject(error)
  }
)

export default apiClient
