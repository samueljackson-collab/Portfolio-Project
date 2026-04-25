import axios, { AxiosError } from 'axios'
import type { ScanSession, ScanCreateRequest, Report } from './types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Response interceptor: normalise errors for callers ──────────────────────
api.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    if (!error.response) {
      // Network error / server unreachable
      return Promise.reject(new Error('Network error: cannot reach the Bug Hunter API'))
    }

    const { status, data } = error.response as { status: number; data: any }

    switch (status) {
      case 401:
        return Promise.reject(new Error('Unauthorized: check your API key (X-API-Key header)'))
      case 413:
        return Promise.reject(new Error('Payload too large: reduce the code size and try again'))
      case 422:
        return Promise.reject(
          new Error((data?.detail as string | undefined) ?? 'Validation error: check your request')
        )
      case 429:
        return Promise.reject(new Error('Rate limit exceeded: please wait before submitting another scan'))
      case 503:
        return Promise.reject(new Error((data?.detail as string | undefined) ?? 'Service temporarily unavailable'))
      default:
        return Promise.reject(
          new Error((data?.detail as string | undefined) ?? `Request failed with status ${status}`)
        )
    }
  }
)

export const scansApi = {
  create: (data: ScanCreateRequest) =>
    api.post<ScanSession>('/scans', data).then(r => r.data),

  get: (id: string) =>
    api.get<ScanSession>(`/scans/${id}`).then(r => r.data),

  list: (params?: { platform?: string; status?: string; limit?: number }) =>
    api.get<ScanSession[]>('/scans', { params }).then(r => r.data),
}

export const reportsApi = {
  list: (params?: { limit?: number }) =>
    api.get<Report[]>('/reports', { params }).then(r => r.data),

  get: (id: string) =>
    api.get<Report>(`/reports/${id}`).then(r => r.data),

  htmlUrl: (id: string) => `/api/reports/${id}/html`,
  pdfUrl: (id: string) => `/api/reports/${id}/pdf`,
}

export const healthApi = {
  check: () => api.get<{ status: string; version: string; db: string }>('/health').then(r => r.data),
}
