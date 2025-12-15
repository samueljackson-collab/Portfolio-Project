import { useEffect, useMemo, useState } from 'react'
import { fetchOverview, login, submitScan } from './api'
import type { Endpoint, Finding, Page } from './types'

interface GroupedFinding {
  endpoint: Endpoint
  pages: Record<number, { page: Page; findings: Finding[] }>
}

export function LoginForm({ onAuthenticated, onError, error }: { onAuthenticated: (token: string) => void; onError: (error: string) => void; error?: string }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const { access_token } = await login(username, password)
      onAuthenticated(access_token)
    } catch (err: any) {
      onError(err.message || 'Login failed')
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Web App Assessment Login</h2>
      <label>
        Username
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
      </label>
      <label>
        Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Sign in</button>
    </form>
  )
}

export function ScanForm({ endpoints, onSubmit }: { endpoints: Endpoint[]; onSubmit: (endpointId: number, url: string) => void }) {
  const [endpointId, setEndpointId] = useState<number>(endpoints[0]?.id || 1)
  const [url, setUrl] = useState('http://example.com/')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(endpointId, url)
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>Scan a page</h3>
      <label>
        Endpoint
        <select value={endpointId} onChange={(e) => setEndpointId(Number(e.target.value))}>
          {endpoints.map((endpoint) => (
            <option key={endpoint.id} value={endpoint.id}>
              {endpoint.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Page URL
        <input value={url} onChange={(e) => setUrl(e.target.value)} />
      </label>
      <button type="submit">Run scan</button>
    </form>
  )
}

export function FindingsList({ grouped }: { grouped: GroupedFinding[] }) {
  return (
    <div className="grid">
      {grouped.map((group) => (
        <div key={group.endpoint.id} className="card">
          <h3>{group.endpoint.name}</h3>
          <p className="muted">{group.endpoint.path}</p>
          {Object.values(group.pages).map(({ page, findings }) => (
            <div key={page.id} className="finding-block">
              <div className="finding-page">{page.url}</div>
              {findings.length === 0 && <p className="muted">No findings yet.</p>}
              <ul>
                {findings.map((finding) => (
                  <li key={finding.id} className={`severity ${finding.severity}`}>
                    <div className="finding-title">{finding.title}</div>
                    <div className="finding-meta">
                      <span>{finding.rule}</span>
                      <span>{new Date(finding.created_at).toLocaleString()}</span>
                    </div>
                    <p>{finding.description}</p>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [token, setToken] = useState<string | null>(null)
  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [pages, setPages] = useState<Page[]>([])
  const [findings, setFindings] = useState<Finding[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) return
    const load = async () => {
      try {
        setLoading(true)
        const overview = await fetchOverview(token)
        setEndpoints(overview.endpoints)
        setPages(overview.pages)
        setFindings(overview.findings)
      } catch (err) {
        setError('Unable to load data. Check your token or API availability.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [token])

  const groupedFindings = useMemo<GroupedFinding[]>(() => {
    return endpoints.map((endpoint) => {
      const pagesForEndpoint = pages.filter((page) => page.endpoint_id === endpoint.id)
      const findingsForEndpoint = findings.filter((finding) => finding.endpoint_id === endpoint.id)
      const byPage: Record<number, { page: Page; findings: Finding[] }> = {}
      pagesForEndpoint.forEach((page) => {
        byPage[page.id] = { page, findings: [] }
      })
      findingsForEndpoint.forEach((finding) => {
        if (!byPage[finding.page_id]) return
        byPage[finding.page_id].findings.push(finding)
      })
      return { endpoint, pages: byPage }
    })
  }, [endpoints, pages, findings])

  const handleLogin = async (tokenValue: string) => {
    setToken(tokenValue)
    setError(null)
  }

  const handleLoginError = (errorMessage: string) => {
    setError(errorMessage)
  }

  const handleScan = async (endpointId: number, url: string) => {
    if (!token) return
    try {
      setLoading(true)
      const response = await submitScan(token, { endpoint_id: endpointId, url })
      setPages((prev) => [...prev, response.page])
      setFindings((prev) => [...prev, ...response.findings])
    } catch (err) {
      setError('Scan failed. Ensure the backend is reachable and your token is valid.')
    } finally {
      setLoading(false)
    }
  }

  const content = token ? (
    <>
      <div className="toolbar">
        <div>
          <h1>Assessment Dashboard</h1>
          <p className="muted">Pages and findings grouped by endpoint.</p>
        </div>
        <button className="link" onClick={() => setToken(null)}>
          Log out
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      <ScanForm endpoints={endpoints} onSubmit={handleScan} />
      {loading && <p className="muted">Loading...</p>}
      {endpoints.length === 0 ? <p>No endpoints loaded yet.</p> : <FindingsList grouped={groupedFindings} />}
    </>
  ) : (
    <LoginForm onAuthenticated={handleLogin} onError={handleLoginError} error={error ?? undefined} />
  )

  return <div className="layout">{content}</div>
}
