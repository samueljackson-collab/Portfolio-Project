import axios from 'axios'
import type { ScanSession, ScanCreateRequest, Report } from './types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

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
  check: () => api.get<{ status: string; version: string }>('/health').then(r => r.data),
}
