import { render, screen, within, fireEvent } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App, { FindingsList, LoginForm } from './App'
import type { Endpoint, Finding, Page } from './types'

vi.mock('./api', () => ({
  login: vi.fn(async () => ({ access_token: 'token' })),
  fetchOverview: vi.fn(async () => ({
    endpoints: [
      { id: 1, name: 'API', path: '/api' },
      { id: 2, name: 'UI', path: '/' }
    ],
    pages: [
      { id: 11, endpoint_id: 1, url: 'https://example.com/api' },
      { id: 21, endpoint_id: 2, url: 'https://example.com/' }
    ],
    findings: [
      {
        id: 100,
        endpoint_id: 1,
        page_id: 11,
        title: 'Insecure transport',
        severity: 'high',
        description: 'Use HTTPS.',
        rule: 'PLAIN_HTTP',
        created_at: new Date().toISOString()
      }
    ]
  })),
  submitScan: vi.fn(async () => ({
    page: { id: 99, endpoint_id: 1, url: 'http://example.com', last_scanned: new Date().toISOString() },
    findings: []
  }))
}))

const sampleEndpoints: Endpoint[] = [
  { id: 1, name: 'API', path: '/api' },
  { id: 2, name: 'UI', path: '/' }
]

const samplePages: Page[] = [
  { id: 1, endpoint_id: 1, url: 'https://example.com/api' },
  { id: 2, endpoint_id: 2, url: 'https://example.com/' }
]

const sampleFindings: Finding[] = [
  {
    id: 5,
    endpoint_id: 1,
    page_id: 1,
    title: 'Debug flag',
    severity: 'medium',
    description: 'Debug parameter detected',
    rule: 'DEBUG_FLAG',
    created_at: new Date().toISOString()
  }
]

describe('FindingsList', () => {
  it('groups findings by endpoint and page', () => {
    render(
      <FindingsList
        grouped={[
          {
            endpoint: sampleEndpoints[0],
            pages: {
              1: { page: samplePages[0], findings: sampleFindings }
            }
          },
          {
            endpoint: sampleEndpoints[1],
            pages: {
              2: { page: samplePages[1], findings: [] }
            }
          }
        ]}
      />
    )

    expect(screen.getByText('API')).toBeInTheDocument()
    const pageBlock = screen.getByText('https://example.com/api').closest('.finding-block')
    expect(pageBlock).toBeTruthy()
    if (pageBlock) {
      expect(within(pageBlock).getByText('Debug flag')).toBeInTheDocument()
    }
  })
})

describe('Login and load flow', () => {
  it('logs in and renders dashboard', async () => {
    render(<App />)
    fireEvent.click(screen.getByText('Sign in'))

    expect(await screen.findByText('Assessment Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Pages and findings grouped by endpoint.')).toBeInTheDocument()
  })

  it('shows validation messages from login form', async () => {
    const onAuthenticated = vi.fn()
    render(<LoginForm onAuthenticated={onAuthenticated} error="Invalid" />)
    expect(screen.getByText('Invalid')).toBeInTheDocument()
  })
})
