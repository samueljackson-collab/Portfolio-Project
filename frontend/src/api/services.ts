/**
 * API Services
 *
 * Service functions for interacting with the backend API
 */

import apiClient from './client'
import type {
  User,
  Content,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  CreateContentRequest,
  UpdateContentRequest,
  Photo,
  Album,
  PhotoListResponse,
  AlbumListResponse,
  PhotoUploadResponse,
  CalendarMonthResponse,
  Operation,
  OperationEvent,
  Incident,
  IncidentEvent,
  SocAlert,
  SocCase,
  SocPlaybook,
  Hypothesis,
  Finding,
  DetectionRule,
  MalwareSample,
  MalwareDetail,
  Endpoint,
  EndpointAlert,
  EndpointPolicy,
  DeploymentSummary,
} from './types'

/**
 * Authentication Services
 */
export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },

  /**
   * Login user and get access token
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },
}

/**
 * Content Services
 */
export const contentService = {
  /**
   * Get all content items with optional pagination
   */
  async getAll(skip = 0, limit = 100): Promise<Content[]> {
    const response = await apiClient.get<Content[]>('/content', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Get a single content item by ID
   */
  async getById(id: string): Promise<Content> {
    const response = await apiClient.get<Content>(`/content/${id}`)
    return response.data
  },

  /**
   * Create a new content item
   */
  async create(data: CreateContentRequest): Promise<Content> {
    const response = await apiClient.post<Content>('/content', data)
    return response.data
  },

  /**
   * Update an existing content item
   */
  async update(id: string, data: UpdateContentRequest): Promise<Content> {
    const response = await apiClient.put<Content>(`/content/${id}`, data)
    return response.data
  },

  /**
   * Delete a content item
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/content/${id}`)
  },
}

/**
 * Health Check Service
 */
export const healthService = {
  /**
   * Check API health status
   */
  async check(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get<{ status: string; timestamp: string }>('/health')
    return response.data
  },
}

/**
 * Photo Services
 */
export const photoService = {
  /**
   * Upload a photo file
   */
  async upload(file: File): Promise<PhotoUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<PhotoUploadResponse>('/photos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Get all photos with optional filtering and pagination
   */
  async getAll(params?: {
    page?: number
    page_size?: number
    album_id?: string
    city?: string
    year?: number
    month?: number
  }): Promise<PhotoListResponse> {
    const response = await apiClient.get<PhotoListResponse>('/photos', { params })
    return response.data
  },

  /**
   * Get a single photo by ID
   */
  async getById(id: string): Promise<Photo> {
    const response = await apiClient.get<Photo>(`/photos/${id}`)
    return response.data
  },

  /**
   * Download a photo or thumbnail as a Blob (preserves auth headers)
   */
  async downloadFile(id: string, thumbnail = false): Promise<Blob> {
    const response = await apiClient.get(`/photos/${id}/file`, {
      params: thumbnail ? { thumbnail: true } : undefined,
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Delete a photo
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/photos/${id}`)
  },

  /**
   * Get calendar view for a specific month
   */
  async getCalendarMonth(year: number, month: number): Promise<CalendarMonthResponse> {
    const response = await apiClient.get<CalendarMonthResponse>(
      `/photos/calendar/${year}/${month}`
    )
    return response.data
  },
}

/**
 * Album Services
 */
export const albumService = {
  /**
   * Get all albums with optional filtering and pagination
   */
  async getAll(params?: {
    page?: number
    page_size?: number
    album_type?: 'location' | 'date' | 'custom'
  }): Promise<AlbumListResponse> {
    const response = await apiClient.get<AlbumListResponse>('/photos/albums', { params })
    return response.data
  },
}

/**
 * Red team simulator services
 */
export const redTeamService = {
  async createOperation(data: { name: string; objective?: string; stealth_factor?: number }) {
    const response = await apiClient.post<Operation>('/red-team/operations', data)
    return response.data
  },
  async listOperations() {
    const response = await apiClient.get<Operation[]>('/red-team/operations')
    return response.data
  },
  async addEvent(operationId: string, data: Partial<OperationEvent>) {
    const response = await apiClient.post<OperationEvent>(`/red-team/operations/${operationId}/events`, data)
    return response.data
  },
  async simulate(operationId: string, seed?: number) {
    const response = await apiClient.post<OperationEvent>(
      `/red-team/operations/${operationId}/simulate-next-day`,
      undefined,
      { params: seed ? { seed } : undefined }
    )
    return response.data
  },
  async timeline(operationId: string, detected?: boolean) {
    const response = await apiClient.get<OperationEvent[]>(`/red-team/operations/${operationId}/timeline`, {
      params: detected !== undefined ? { detected } : undefined,
    })
    return response.data
  },
}

/**
 * Ransomware response services
 */
export const ransomwareService = {
  async createIncident(data: { name: string; severity?: string }) {
    const response = await apiClient.post<Incident>('/incidents', data)
    return response.data
  },
  async listIncidents() {
    const response = await apiClient.get<Incident[]>('/incidents')
    return response.data
  },
  async simulate(incidentId: string) {
    const response = await apiClient.post<Incident>(`/incidents/${incidentId}/simulate`)
    return response.data
  },
  async timeline(incidentId: string) {
    const response = await apiClient.get<IncidentEvent[]>(`/incidents/${incidentId}/timeline`)
    return response.data
  },
}

/**
 * SOC portal services
 */
export const socService = {
  async listPlaybooks() {
    const response = await apiClient.get<SocPlaybook[]>('/soc/playbooks')
    return response.data
  },
  async generateAlerts() {
    const response = await apiClient.post<SocAlert[]>('/soc/alerts/generate')
    return response.data
  },
  async listAlerts() {
    const response = await apiClient.get<SocAlert[]>('/soc/alerts')
    return response.data
  },
  async createCase(data: { title: string; alert_ids?: string[] }) {
    const response = await apiClient.post<SocCase>('/soc/cases', data)
    return response.data
  },
  async listCases() {
    const response = await apiClient.get<SocCase[]>('/soc/cases')
    return response.data
  },
}

/**
 * Threat hunting services
 */
export const huntingService = {
  async listHypotheses() {
    const response = await apiClient.get<Hypothesis[]>('/threat-hunting/hypotheses')
    return response.data
  },
  async createHypothesis(data: { title: string; description?: string }) {
    const response = await apiClient.post<Hypothesis>('/threat-hunting/hypotheses', data)
    return response.data
  },
  async addFinding(hypothesisId: string, data: { severity: string; details: string }) {
    const response = await apiClient.post<Finding>(`/threat-hunting/hypotheses/${hypothesisId}/findings`, data)
    return response.data
  },
  async listFindings(hypothesisId: string) {
    const response = await apiClient.get<Finding[]>(`/threat-hunting/hypotheses/${hypothesisId}/findings`)
    return response.data
  },
  async promoteFinding(findingId: string) {
    const response = await apiClient.post<DetectionRule>(`/threat-hunting/findings/${findingId}/promote`)
    return response.data
  },
  async listRules(status?: string) {
    const response = await apiClient.get<DetectionRule[]>('/threat-hunting/detection-rules', {
      params: status ? { status } : undefined,
    })
    return response.data
  },
}

/**
 * Malware analysis services
 */
export const malwareService = {
  async createSample(data: { name: string; file_hash: string; sample_type?: string }) {
    const response = await apiClient.post<MalwareSample>('/malware/samples', data)
    return response.data
  },
  async listSamples() {
    const response = await apiClient.get<MalwareSample[]>('/malware/samples')
    return response.data
  },
  async analyze(sampleId: string) {
    const response = await apiClient.post<MalwareDetail>(`/malware/samples/${sampleId}/analyze`)
    return response.data
  },
}

/**
 * EDR simulation services
 */
export const edrService = {
  async registerEndpoint(data: { hostname: string; operating_system: string; agent_version: string }) {
    const response = await apiClient.post<Endpoint>('/edr/endpoints', data)
    return response.data
  },
  async listEndpoints() {
    const response = await apiClient.get<Endpoint[]>('/edr/endpoints')
    return response.data
  },
  async listAlerts() {
    const response = await apiClient.get<EndpointAlert[]>('/edr/alerts')
    return response.data
  },
  async listPolicies() {
    const response = await apiClient.get<EndpointPolicy[]>('/edr/policies')
    return response.data
  },
  async togglePolicy(policyId: string, enabled: boolean) {
    const response = await apiClient.patch<EndpointPolicy>(`/edr/policies/${policyId}`, { enabled })
    return response.data
  },
  async deploymentSummary() {
    const response = await apiClient.get<DeploymentSummary>('/edr/deployment/summary')
    return response.data
  },
}

/**
 * Orchestration Services
 */
export const orchestrationService = {
  /**
   * List available deployment plans
   */
  async listPlans() {
    const response = await apiClient.get<import('./types').OrchestrationPlan[]>(
      '/orchestration/plans'
    )
    return response.data
  },

  /**
   * Trigger a new orchestration run
   */
  async startRun(payload: import('./types').OrchestrationRunRequest) {
    const response = await apiClient.post<import('./types').OrchestrationRun>(
      '/orchestration/runs',
      payload
    )
    return response.data
  },

  /**
   * Get historical orchestration runs
   */
  async listRuns() {
    const response = await apiClient.get<import('./types').OrchestrationRun[]>(
      '/orchestration/runs'
    )
    return response.data
  },

  /**
   * Get details for a specific run
   */
  async getRun(runId: string) {
    const response = await apiClient.get<import('./types').OrchestrationRun>(
      `/orchestration/runs/${runId}`
    )
    return response.data
  }
}
