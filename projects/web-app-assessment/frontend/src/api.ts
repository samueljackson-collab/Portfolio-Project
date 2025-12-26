import axios from 'axios'
import type { Endpoint, Page, Finding, ScanPayload, ScanResponse } from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Attempts to log in with the provided username and password.
 * Throws an error if the request fails (e.g., network error, invalid credentials).
 */
export async function login(username: string, password: string) {
  try {
    const response = await axios.post(`${API_URL}/login`, { username, password })
    return response.data as { access_token: string }
  } catch (error: any) {
    throw new Error(
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      'Login failed'
    )
  }
}

export async function fetchOverview(token: string) {
  const headers = { Authorization: `Bearer ${token}` }
  const [endpoints, pages, findings] = await Promise.all([
    axios.get(`${API_URL}/endpoints`, { headers }),
    axios.get(`${API_URL}/pages`, { headers }),
    axios.get(`${API_URL}/findings`, { headers })
  ])
  return {
    endpoints: endpoints.data as Endpoint[],
    pages: pages.data as Page[],
    findings: findings.data as Finding[]
  }
}

export async function submitScan(token: string, payload: ScanPayload) {
  const headers = { Authorization: `Bearer ${token}` }
  const response = await axios.post(`${API_URL}/scan-page`, payload, { headers })
  return response.data as ScanResponse
}
