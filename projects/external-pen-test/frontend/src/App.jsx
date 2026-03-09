import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000' })

function useToken() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }, [token])
  return [token, setToken]
}

const Protected = ({ token, children }) => {
  if (!token) {
    return <p>Please authenticate to manage targets.</p>
  }
  return children
}

export default function App() {
  const [token, setToken] = useToken()
  const [targets, setTargets] = useState([])
  const [targetForm, setTargetForm] = useState({ name: '', description: '', url: '', environment: 'production' })
  const [findingForm, setFindingForm] = useState({ title: '', description: '', severity: 'medium', target_id: '' })
  const [scanTarget, setScanTarget] = useState('')
  const authHeader = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token])

  const login = async (e) => {
    e.preventDefault()
    const data = new FormData(e.target)
    const res = await api.post('/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    setToken(res.data.access_token)
  }

  const register = async (e) => {
    e.preventDefault()
    const payload = {
      username: e.target.username.value,
      password: e.target.password.value,
      role: 'analyst'
    }
    await api.post('/auth/register', payload)
    await login(e)
  }

  const fetchTargets = async () => {
    if (!token) return
    const res = await api.get('/targets', { headers: authHeader })
    setTargets(res.data)
  }

  useEffect(() => {
    fetchTargets()
  }, [token])

  const submitTarget = async (e) => {
    e.preventDefault()
    const res = await api.post('/targets', targetForm, { headers: authHeader })
    setTargets((prev) => [...prev, res.data])
    setTargetForm({ name: '', description: '', url: '', environment: 'production' })
  }

  const submitFinding = async (e) => {
    e.preventDefault()
    await api.post('/findings', findingForm, { headers: authHeader })
    setFindingForm({ title: '', description: '', severity: 'medium', target_id: '' })
  }

  const runScan = async (e) => {
    e.preventDefault()
    await api.post('/scan', { target_id: parseInt(scanTarget, 10) }, { headers: authHeader })
    setScanTarget('')
  }

  return (
    <div className="app">
      <nav>
        <h1>External Pen Test Portal</h1>
        {token && <button onClick={() => setToken('')}>Logout</button>}
      </nav>
      {!token && (
        <div className="card">
          <h2>Authenticate</h2>
          <form onSubmit={login}>
            <label htmlFor="username">Username</label>
            <input name="username" id="username" placeholder="analyst" required />
            <label htmlFor="password">Password</label>
            <input type="password" name="password" id="password" placeholder="password123" required />
            <button type="submit">Login</button>
          </form>
          <p style={{ marginTop: '1rem' }}>New analyst? Register below.</p>
          <form onSubmit={register}>
            <label htmlFor="reg-username">Username</label>
            <input name="username" id="reg-username" required />
            <label htmlFor="reg-password">Password</label>
            <input type="password" name="password" id="reg-password" required />
            <button type="submit">Register</button>
          </form>
        </div>
      )}

      <Protected token={token}>
        <div className="card">
          <h2>Create Target</h2>
          <form onSubmit={submitTarget}>
            <label htmlFor="target-name">Name</label>
            <input id="target-name" value={targetForm.name} onChange={(e) => setTargetForm({ ...targetForm, name: e.target.value })} required />
            <label>Description</label>
            <textarea
              value={targetForm.description}
              onChange={(e) => setTargetForm({ ...targetForm, description: e.target.value })}
            />
            <label>URL</label>
            <input value={targetForm.url} onChange={(e) => setTargetForm({ ...targetForm, url: e.target.value })} required />
            <label>Environment</label>
            <input
              value={targetForm.environment}
              onChange={(e) => setTargetForm({ ...targetForm, environment: e.target.value })}
            />
            <button type="submit">Create Target</button>
          </form>
        </div>

        <div className="card">
          <h2>Report Finding</h2>
          <form onSubmit={submitFinding}>
            <label>Title</label>
            <input
              value={findingForm.title}
              onChange={(e) => setFindingForm({ ...findingForm, title: e.target.value })}
              required
            />
            <label>Description</label>
            <textarea
              value={findingForm.description}
              onChange={(e) => setFindingForm({ ...findingForm, description: e.target.value })}
              required
            />
            <label>Severity</label>
            <input
              value={findingForm.severity}
              onChange={(e) => setFindingForm({ ...findingForm, severity: e.target.value })}
              required
            />
            <label>Target</label>
            <select
              value={findingForm.target_id}
              onChange={(e) => setFindingForm({ ...findingForm, target_id: parseInt(e.target.value, 10) })}
              required
            >
              <option value="">Select a target</option>
              {targets.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
            <button type="submit">Save Finding</button>
          </form>
        </div>

        <div className="card">
          <h2>Trigger Scan</h2>
          <form onSubmit={runScan}>
            <label>Target ID</label>
            <input value={scanTarget} onChange={(e) => setScanTarget(e.target.value)} required />
            <button type="submit">Run Automated Scan</button>
          </form>
        </div>
      </Protected>
    </div>
  )
}
