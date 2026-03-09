/**
 * Authentication Context
 *
 * Provides authentication state and functions to any component in the tree
 * via the React Context API. Wrap your app with <AuthProvider> at the root
 * level, then call useAuth() anywhere you need the current user or auth actions.
 *
 * TOKEN STORAGE DECISION — WHY localStorage?
 * We store the JWT in localStorage rather than in an HTTP-only cookie because
 * the current backend does not set cookies. localStorage makes the token
 * accessible to the Axios client (client.ts) so it can attach the
 * Authorization header on every request.
 *
 * TRADE-OFF: localStorage is accessible to JavaScript, which means it is
 * vulnerable to XSS attacks if malicious scripts run on the page. HTTP-only
 * cookies are generally considered more secure for production apps because
 * JS cannot read them. For this portfolio application the XSS risk is low
 * (no user-generated HTML is rendered unescaped), but a production system
 * should migrate to HTTP-only cookies + CSRF tokens.
 *
 * FLOW OVERVIEW:
 *   1. App mounts → AuthProvider reads token from localStorage
 *   2. If a token exists, we make a network call to verify it is still valid
 *      (tokens can expire server-side even if they are stored locally)
 *   3. If valid: hydrate user state from the fresh API response
 *   4. If invalid/expired: clear storage and set user = null (unauthenticated)
 *   5. login() → POST /auth/login → store token → GET /auth/me → store user
 *   6. register() → POST /auth/register → immediately calls login() so the
 *      user lands on the dashboard without a separate login step
 *   7. logout() → remove token and user from localStorage + clear React state
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, type User, type LoginRequest, type RegisterRequest } from '../api'

interface AuthContextType {
  user: User | null
  token: string | null
  /** Derived convenience flag: true only when BOTH user and token are set. */
  isAuthenticated: boolean
  /** True during the initial localStorage → API verification on mount. */
  isLoading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

/**
 * AuthProvider — wraps the application and makes auth state available to all
 * descendant components via the useAuth() hook.
 *
 * Mount this at the root of the app (see App.tsx) so all routes have access.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  // isLoading starts as TRUE so ProtectedRoute shows a spinner instead of a
  // flash of the login page while we verify the stored token on mount.
  const [isLoading, setIsLoading] = useState(true)

  /**
   * On mount: attempt to restore a previous session from localStorage.
   *
   * WHY WE MAKE A NETWORK CALL HERE:
   * localStorage can contain an expired or revoked JWT. Parsing the local user
   * JSON would incorrectly show the user as logged in even after the token has
   * expired server-side. The GET /auth/me call validates the token and returns
   * up-to-date user data (e.g. if the email was changed on another device).
   *
   * We set state optimistically from localStorage first (so there is no flicker
   * if the token is valid), then overwrite with the server response.
   */
  useEffect(() => {
    const loadUser = async () => {
      const storedToken = localStorage.getItem('access_token')
      const storedUser = localStorage.getItem('user')

      if (storedToken && storedUser) {
        try {
          // Optimistic update: show user immediately while we verify the token
          setToken(storedToken)
          setUser(JSON.parse(storedUser))

          // Verify the token is still valid — if the server returns 401 the
          // Axios interceptor in client.ts will clear localStorage and redirect
          // to /login. If it returns 200 we get fresh user data.
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
          localStorage.setItem('user', JSON.stringify(currentUser))
        } catch (error) {
          // Token invalid or network error — treat as logged out.
          // The 401 case is already handled by the Axios interceptor, but we
          // clear state here too for safety in case the error is non-401.
          console.error('Session restore failed:', error)
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          setToken(null)
          setUser(null)
        }
      }

      // Always set isLoading to false so the UI unblocks, even on error.
      setIsLoading(false)
    }

    loadUser()
  }, [])

  /**
   * login — authenticates the user and persists their session.
   *
   * FLOW: POST /auth/login (form-encoded) → receive JWT → GET /auth/me →
   * store both token and user in localStorage and React state.
   *
   * We call GET /auth/me after login (rather than decoding the JWT locally)
   * because the server is the authoritative source of user data. Decoding a
   * JWT client-side without verifying the signature is not safe.
   *
   * Errors are re-thrown so the Login page can display them to the user.
   */
  const login = async (credentials: LoginRequest) => {
    setIsLoading(true)
    try {
      const response = await authService.login(credentials)

      // Store token first — the subsequent getCurrentUser() call needs it to
      // attach the Authorization header (via the Axios request interceptor).
      localStorage.setItem('access_token', response.access_token)
      setToken(response.access_token)

      const userData = await authService.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
    } catch (error) {
      console.error('Login failed:', error)
      throw error // propagate to Login.tsx for form error display
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * register — creates a new account then immediately logs the user in.
   *
   * WHY AUTO-LOGIN: Forcing a user to fill in the login form again right after
   * registration is poor UX. Since we already have their credentials in hand,
   * we call login() immediately so they land on the dashboard automatically.
   *
   * Errors are re-thrown so the Register page can display them to the user.
   */
  const register = async (data: RegisterRequest) => {
    setIsLoading(true)
    try {
      await authService.register(data)
      // Auto-login with the same credentials — login() handles its own
      // isLoading state, so we don't need to set it again here.
      await login({
        username: data.email,
        password: data.password,
      })
    } catch (error) {
      console.error('Registration failed:', error)
      throw error // propagate to Register.tsx for form error display
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * logout — clears all auth state from both localStorage and React.
   *
   * No API call is needed because our JWTs are stateless (no server-side
   * session to invalidate). Simply removing the token from storage is enough
   * to prevent it from being sent on future requests.
   *
   * NOTE: If you add token revocation/blocklisting to the backend in the
   * future, add a POST /auth/logout call here.
   */
  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    // Both must be truthy — a token without a user object (or vice versa)
    // indicates an inconsistent state that should be treated as unauthenticated.
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * useAuth — hook to consume the authentication context.
 *
 * Must be called inside a component that is a descendant of <AuthProvider>.
 * Throws a descriptive error if called outside the provider so the cause is
 * immediately obvious during development.
 *
 * @example
 *   const { user, isAuthenticated, logout } = useAuth()
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
