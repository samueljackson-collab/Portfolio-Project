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
 * Red Team Simulator Services
 *
 * These endpoints drive the Red Team Operation Simulator on the Security
 * Simulators page. The backend models an APT (Advanced Persistent Threat)
 * actor moving through an environment over a configurable number of days.
 *
 * Each simulated "day" produces an OperationEvent with a category (recon,
 * lateral movement, exfiltration, etc.) and a `detected` flag indicating
 * whether the blue team caught the activity.
 */
export const redTeamService = {
  /**
   * Create a new red team operation.
   * @param data.name       Human-readable label shown in the timeline header
   * @param data.objective  Free-text goal description (shown in tooltips)
   * @param data.stealth_factor  0–1 float controlling how likely events are
   *                             to evade detection (higher = stealthier)
   */
  async createOperation(data: { name: string; objective?: string; stealth_factor?: number }): Promise<Operation> {
    const response = await apiClient.post<Operation>('/red-team/operations', data)
    return response.data
  },

  /** Returns all operations stored in the backend's in-memory list. */
  async listOperations(): Promise<Operation[]> {
    const response = await apiClient.get<Operation[]>('/red-team/operations')
    return response.data
  },

  /**
   * Manually add a specific event to an operation (advanced use — the UI
   * primarily uses `simulate` instead).
   */
  async addEvent(operationId: string, data: Partial<OperationEvent>): Promise<OperationEvent> {
    const response = await apiClient.post<OperationEvent>(`/red-team/operations/${operationId}/events`, data)
    return response.data
  },

  /**
   * Advance the operation by one simulated day, generating a random event.
   * @param seed  Optional integer for deterministic event generation (useful
   *              for consistent demo output — seed=3 is used in SecuritySimulators.tsx)
   */
  async simulate(operationId: string, seed?: number): Promise<OperationEvent> {
    const response = await apiClient.post<OperationEvent>(
      `/red-team/operations/${operationId}/simulate-next-day`,
      undefined,
      { params: seed ? { seed } : undefined }
    )
    return response.data
  },

  /**
   * Fetch the event timeline for an operation, optionally filtered to only
   * show detected (or undetected) events.
   */
  async timeline(operationId: string, detected?: boolean): Promise<OperationEvent[]> {
    const response = await apiClient.get<OperationEvent[]>(`/red-team/operations/${operationId}/timeline`, {
      params: detected !== undefined ? { detected } : undefined,
    })
    return response.data
  },
}

/**
 * Ransomware Response Services
 *
 * Simulates the lifecycle of a ransomware incident from initial infection
 * through containment and recovery. Each incident produces an ordered list
 * of IncidentEvents representing the stages (e.g. "Encryption started",
 * "Backup validation", "Systems restored").
 */
export const ransomwareService = {
  /**
   * Create a new ransomware incident.
   * @param data.name      Label shown in the incident card header
   * @param data.severity  'low' | 'medium' | 'high' | 'critical' (default: 'high')
   */
  async createIncident(data: { name: string; severity?: string }): Promise<Incident> {
    const response = await apiClient.post<Incident>('/incidents', data)
    return response.data
  },

  /** Returns all incidents stored in the backend's in-memory list. */
  async listIncidents(): Promise<Incident[]> {
    const response = await apiClient.get<Incident[]>('/incidents')
    return response.data
  },

  /**
   * Run the full ransomware lifecycle simulation for an incident.
   * Returns the updated incident with all events populated.
   */
  async simulate(incidentId: string): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${incidentId}/simulate`)
    return response.data
  },

  /** Fetch the raw event list for an incident (subset of the Incident object). */
  async timeline(incidentId: string): Promise<IncidentEvent[]> {
    const response = await apiClient.get<IncidentEvent[]>(`/incidents/${incidentId}/timeline`)
    return response.data
  },
}

/**
 * SOC Portal Services
 *
 * Models a Security Operations Centre workflow: playbooks define how to
 * respond to alert types, alerts are generated by the simulator or ingested
 * from real sources, and cases group related alerts for analyst triage.
 */
export const socService = {
  /** Returns all available response playbooks (e.g. "Phishing Response"). */
  async listPlaybooks(): Promise<SocPlaybook[]> {
    const response = await apiClient.get<SocPlaybook[]>('/soc/playbooks')
    return response.data
  },

  /**
   * Ask the backend to produce a fresh batch of synthetic alerts and replace
   * the current alert list. Used in the UI's "Generate Alerts" button.
   */
  async generateAlerts(): Promise<SocAlert[]> {
    const response = await apiClient.post<SocAlert[]>('/soc/alerts/generate')
    return response.data
  },

  /** Returns the current alert queue (alerts that have been generated or ingested). */
  async listAlerts(): Promise<SocAlert[]> {
    const response = await apiClient.get<SocAlert[]>('/soc/alerts')
    return response.data
  },

  /**
   * Group one or more alerts into a case for coordinated investigation.
   * @param data.alert_ids  Optional list of alert IDs to link to the new case
   */
  async createCase(data: { title: string; alert_ids?: string[] }): Promise<SocCase> {
    const response = await apiClient.post<SocCase>('/soc/cases', data)
    return response.data
  },

  /** Returns all open and closed cases. */
  async listCases(): Promise<SocCase[]> {
    const response = await apiClient.get<SocCase[]>('/soc/cases')
    return response.data
  },
}

/**
 * Threat Hunting Services
 *
 * Models the analyst-driven hypothesis → finding → detection rule pipeline.
 * An analyst forms a Hypothesis (e.g. "Lateral movement via WinRM"), hunts
 * for evidence, records Findings, and promotes high-confidence findings into
 * draft DetectionRules that can be deployed to a SIEM.
 */
export const huntingService = {
  /** Returns all hypotheses in the system. */
  async listHypotheses(): Promise<Hypothesis[]> {
    const response = await apiClient.get<Hypothesis[]>('/threat-hunting/hypotheses')
    return response.data
  },

  /**
   * Create a new threat hunting hypothesis.
   * @param data.title        Short label — shown as the hypothesis card title
   * @param data.description  Free-text detail about what the analyst is hunting
   */
  async createHypothesis(data: { title: string; description?: string }): Promise<Hypothesis> {
    const response = await apiClient.post<Hypothesis>('/threat-hunting/hypotheses', data)
    return response.data
  },

  /**
   * Attach a finding to an existing hypothesis.
   * @param data.severity  'low' | 'medium' | 'high' | 'critical'
   * @param data.details   Evidence description (e.g. log line, artifact path)
   */
  async addFinding(hypothesisId: string, data: { severity: string; details: string }): Promise<Finding> {
    const response = await apiClient.post<Finding>(`/threat-hunting/hypotheses/${hypothesisId}/findings`, data)
    return response.data
  },

  /** Returns all findings attached to a hypothesis. */
  async listFindings(hypothesisId: string): Promise<Finding[]> {
    const response = await apiClient.get<Finding[]>(`/threat-hunting/hypotheses/${hypothesisId}/findings`)
    return response.data
  },

  /**
   * Promote a finding into a draft DetectionRule.
   * This is the key workflow step: a validated finding becomes an actionable
   * rule that can be reviewed and deployed to a SIEM.
   */
  async promoteFinding(findingId: string): Promise<DetectionRule> {
    const response = await apiClient.post<DetectionRule>(`/threat-hunting/findings/${findingId}/promote`)
    return response.data
  },

  /**
   * Returns all detection rules, optionally filtered by status.
   * @param status  'draft' | 'active' | 'disabled' — omit to get all statuses
   */
  async listRules(status?: string): Promise<DetectionRule[]> {
    const response = await apiClient.get<DetectionRule[]>('/threat-hunting/detection-rules', {
      params: status ? { status } : undefined,
    })
    return response.data
  },
}

/**
 * Malware Analysis Lab Services
 *
 * Simulates the intake and analysis workflow of a malware reverse-engineering
 * lab. A sample is registered with its hash and type, then `analyze()` runs
 * a simulated static/dynamic analysis pipeline and returns a report with
 * findings and a generated YARA detection rule.
 */
export const malwareService = {
  /**
   * Register a malware sample for analysis.
   * @param data.name         Human-readable label (e.g. 'locker-sim')
   * @param data.file_hash    SHA256 or MD5 hash of the file (can be synthetic for demos)
   * @param data.sample_type  'pe' | 'elf' | 'macho' | 'script' | 'document'
   */
  async createSample(data: { name: string; file_hash: string; sample_type?: string }): Promise<MalwareSample> {
    const response = await apiClient.post<MalwareSample>('/malware/samples', data)
    return response.data
  },

  /** Returns all registered malware samples. */
  async listSamples(): Promise<MalwareSample[]> {
    const response = await apiClient.get<MalwareSample[]>('/malware/samples')
    return response.data
  },

  /**
   * Run simulated static + dynamic analysis on a sample and return a report.
   * The report includes static indicators (imports, strings, entropy), dynamic
   * behaviour (network calls, file writes), and a generated YARA rule.
   */
  async analyze(sampleId: string): Promise<MalwareDetail> {
    const response = await apiClient.post<MalwareDetail>(`/malware/samples/${sampleId}/analyze`)
    return response.data
  },
}

/**
 * EDR (Endpoint Detection and Response) Simulation Services
 *
 * Models an enterprise EDR deployment. Endpoints register their agent version,
 * the platform tracks coverage metrics, and security policies can be toggled
 * per-endpoint. The deployment summary provides a high-level view of coverage
 * percentage and outdated agent counts.
 */
export const edrService = {
  /**
   * Register a new endpoint with the EDR platform.
   * @param data.hostname          Machine name shown in the endpoint table
   * @param data.operating_system  'linux' | 'windows' | 'macos'
   * @param data.agent_version     Semver string — agents on major v1 are flagged
   *                               as outdated by the UI to demo upgrade workflows
   */
  async registerEndpoint(data: { hostname: string; operating_system: string; agent_version: string }): Promise<Endpoint> {
    const response = await apiClient.post<Endpoint>('/edr/endpoints', data)
    return response.data
  },

  /** Returns all registered endpoints and their current status. */
  async listEndpoints(): Promise<Endpoint[]> {
    const response = await apiClient.get<Endpoint[]>('/edr/endpoints')
    return response.data
  },

  /** Returns all EDR-generated alerts (threats detected on endpoints). */
  async listAlerts(): Promise<EndpointAlert[]> {
    const response = await apiClient.get<EndpointAlert[]>('/edr/alerts')
    return response.data
  },

  /** Returns all security policies available for deployment. */
  async listPolicies(): Promise<EndpointPolicy[]> {
    const response = await apiClient.get<EndpointPolicy[]>('/edr/policies')
    return response.data
  },

  /**
   * Enable or disable a security policy.
   * @param policyId  UUID of the policy to modify
   * @param enabled   true = enable, false = disable
   */
  async togglePolicy(policyId: string, enabled: boolean): Promise<EndpointPolicy> {
    const response = await apiClient.patch<EndpointPolicy>(`/edr/policies/${policyId}`, { enabled })
    return response.data
  },

  /**
   * Returns aggregate deployment metrics: total endpoints, online count,
   * outdated agent count, and coverage percentage.
   */
  async deploymentSummary(): Promise<DeploymentSummary> {
    const response = await apiClient.get<DeploymentSummary>('/edr/deployment/summary')
    return response.data
  },
}

/**
 * Orchestration Services
 *
 * Drives the Orchestration Console page. Plans define reusable deployment
 * templates (Terraform workspace + Ansible playbook + runbook). Runs record
 * each execution with audit metadata (who requested it, change ticket, timestamps).
 *
 * NOTE: The backend stores runs in memory — they are cleared on server restart.
 * This is intentional for a portfolio demo; production use would persist to a DB.
 */
export const orchestrationService = {
  /**
   * List available deployment plans.
   * Returns the three pre-configured plans: dev-apply, staging-bluegreen,
   * prod-controlled. Plans are defined in orchestration_service.py and do
   * not change at runtime.
   */
  async listPlans(): Promise<OrchestrationPlan[]> {
    const response = await apiClient.get<OrchestrationPlan[]>('/orchestration/plans')
    return response.data
  },

  /**
   * Trigger a new orchestration run for a given plan.
   * The backend validates the plan ID, builds an audit record, and returns
   * immediately with status 'succeeded' (dry-run behaviour for the demo).
   */
  async startRun(payload: OrchestrationRunRequest): Promise<OrchestrationRun> {
    const response = await apiClient.post<OrchestrationRun>('/orchestration/runs', payload)
    return response.data
  },

  /**
   * Get historical orchestration runs, sorted newest-first.
   * Used to populate the Run History table in the console.
   */
  async listRuns(): Promise<OrchestrationRun[]> {
    const response = await apiClient.get<OrchestrationRun[]>('/orchestration/runs')
    return response.data
  },

  /**
   * Get details for a specific run by its UUID.
   * Includes logs, artifact paths, and summary text.
   */
  async getRun(runId: string): Promise<OrchestrationRun> {
    const response = await apiClient.get<OrchestrationRun>(`/orchestration/runs/${runId}`)
    return response.data
  },
}
