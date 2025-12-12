export interface Endpoint {
  id: number
  name: string
  path: string
  description?: string
}

export interface Page {
  id: number
  endpoint_id: number
  url: string
  last_scanned?: string
}

export interface Finding {
  id: number
  endpoint_id: number
  page_id: number
  title: string
  severity: string
  description: string
  rule: string
  created_at: string
}

export interface ScanPayload {
  endpoint_id: number
  url: string
}

export interface ScanResponse {
  page: Page
  findings: Finding[]
}
