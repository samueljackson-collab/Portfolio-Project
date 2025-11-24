import apiClient from './client'

type RoamingSessionPayload = {
  imsi: string
  home_network: string
  visited_network: string
  roaming_enabled?: boolean
}

type RoamingEventPayload = {
  type: string
  message: string
}

export type RoamingSession = {
  session_id: string
  imsi: string
  home_network: string
  visited_network: string
  state: string
  events: { type: string; message: string; timestamp: string }[]
  created_at: string
  updated_at: string
}

export type RoamingAgreements = Record<string, string[]>

export const roamingApi = {
  async listAgreements(): Promise<RoamingAgreements> {
    const { data } = await apiClient.get('/roaming/agreements')
    return data.agreements
  },

  async createSession(payload: RoamingSessionPayload): Promise<RoamingSession> {
    const { data } = await apiClient.post('/roaming/sessions', payload)
    return data
  },

  async addEvent(sessionId: string, payload: RoamingEventPayload): Promise<RoamingSession> {
    const { data } = await apiClient.post(`/roaming/sessions/${sessionId}/events`, payload)
    return data
  },

  async getSession(sessionId: string): Promise<RoamingSession> {
    const { data } = await apiClient.get(`/roaming/sessions/${sessionId}`)
    return data
  },
}

