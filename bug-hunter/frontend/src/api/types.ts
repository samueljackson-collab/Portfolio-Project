export type Platform = 'android' | 'ios' | 'windows' | 'macos' | 'web'
export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'
export type ScanStatus = 'pending' | 'running' | 'complete' | 'failed'

export interface BugFinding {
  id: string
  session_id: string
  title: string
  description: string
  severity: Severity
  category: string
  platform: string
  line_number: number | null
  code_snippet: string
  recommendation: string
  cwe_id: string | null
  cvss_score: number | null
  evidence: string
}

export interface ScanSession {
  id: string
  platform: Platform
  filename: string
  language: string
  status: ScanStatus
  created_at: string
  completed_at: string | null
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  risk_score: number
  findings?: BugFinding[]
}

export interface Report {
  id: string
  session_id: string
  generated_at: string
  executive_summary: string
  total_findings: number
  risk_score: number
  html_content?: string
}

export interface ScanCreateRequest {
  platform: Platform
  filename: string
  code_content: string
  scan_options?: Record<string, unknown>
}
