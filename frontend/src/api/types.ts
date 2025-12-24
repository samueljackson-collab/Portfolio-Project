/**
 * API Type Definitions
 *
 * TypeScript interfaces for API requests and responses
 */

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Content {
  id: string
  title: string
  body: string | null
  owner_id: string
  is_published: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface CreateContentRequest {
  title: string
  body?: string
  is_published?: boolean
}

export interface UpdateContentRequest {
  title?: string
  body?: string
  is_published?: boolean
}

export interface ApiError {
  detail: string | Record<string, unknown>[]
}

// Photo and Album Types

export interface Photo {
  id: string
  owner_id: string
  album_id: string | null
  filename: string
  file_path: string
  thumbnail_path: string | null
  file_size: number
  mime_type: string
  width: number | null
  height: number | null
  capture_date: string | null
  upload_date: string
  latitude: number | null
  longitude: number | null
  city: string | null
  state: string | null
  country: string | null
  camera_make: string | null
  camera_model: string | null
  created_at: string
  updated_at: string
}

export interface Album {
  id: string
  owner_id: string
  name: string
  type: 'location' | 'date' | 'custom'
  photo_count: number
  cover_photo_id: string | null
  created_at: string
  updated_at: string
}

export interface PhotoListResponse {
  items: Photo[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface AlbumListResponse {
  items: Album[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface PhotoUploadResponse {
  photo: Photo
  album: Album | null
  message: string
}

export interface CalendarDateResponse {
  date: string
  photo_count: number
  preview_photos: Photo[]
}

export interface CalendarMonthResponse {
  year: number
  month: number
  dates: CalendarDateResponse[]
  total_photos: number
}

export interface OrchestrationPlan {
  id: string
  name: string
  environment: string
  description: string
  playbook_path: string
  tfvars_file: string
  runbook: string
}

export interface OrchestrationRunRequest {
  plan_id: string
  parameters?: Record<string, string>
}

export interface OrchestrationRun {
  id: string
  plan_id: string
  environment: string
  status: 'running' | 'succeeded' | 'failed'
  requested_by: string
  parameters: Record<string, string>
  started_at: string
  finished_at: string | null
  logs: string[]
  artifacts: Record<string, string>
  summary?: string
}

// Project 5 - Red team simulator
export interface OperationEvent {
  id: string
  operation_id: string
  day: number
  timestamp: string
  description: string
  category: string
  detected: boolean
  detection_confidence: number
}

export interface Operation {
  id: string
  name: string
  objective?: string | null
  stealth_factor: number
  days_elapsed: number
  undetected_streak: number
  first_detection_at?: string | null
  status: string
  events: OperationEvent[]
}

// Project 6 - Ransomware response
export interface IncidentEvent {
  id: string
  incident_id: string
  sequence: number
  type: string
  details: string
  timestamp: string
}

export interface Incident {
  id: string
  name: string
  status: string
  severity: string
  created_at: string
  resolved_at?: string | null
  events: IncidentEvent[]
  warning?: string | null
}

// Project 7 - SOC portal
export interface SocAlert {
  id: string
  title: string
  description: string
  severity: string
  status: string
  source: string
  created_at: string
  updated_at: string
}

export interface SocCase {
  id: string
  title: string
  status: string
  assigned_to?: string | null
  playbook_id?: string | null
  alerts: SocAlert[]
}

export interface SocPlaybook {
  id: string
  name: string
  description?: string | null
  steps?: string[] | null
}

// Project 8 - Threat hunting
export interface Hypothesis {
  id: string
  title: string
  description?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface Finding {
  id: string
  hypothesis_id: string
  severity: string
  details: string
  status: string
  created_at: string
}

export interface DetectionRule {
  id: string
  name: string
  query: string
  status: string
  source_finding_id?: string | null
  created_at: string
}

// Project 9 - Malware analysis
export interface MalwareSample {
  id: string
  name: string
  file_hash: string
  sample_type: string
  family?: string | null
  status: string
  created_at: string
}

export interface AnalysisReport {
  id: string
  sample_id: string
  static_analysis: string
  dynamic_analysis: string
  iocs?: string[]
  yara_rule: string
  created_at: string
}

export interface MalwareDetail {
  sample: MalwareSample
  report?: AnalysisReport | null
}

// Project 10 - EDR simulation
export interface Endpoint {
  id: string
  hostname: string
  operating_system: string
  agent_version: string
  last_checkin: string
  online: boolean
  created_at: string
  updated_at: string
}

export interface EndpointPolicy {
  id: string
  name: string
  description?: string | null
  enabled: boolean
}

export interface EndpointAlert {
  id: string
  endpoint_id?: string | null
  severity: string
  status: string
  description: string
  created_at: string
}

export interface DeploymentSummary {
  total_endpoints: number
  online: number
  outdated_agents: number
  coverage: number
  active_policies: number
}
