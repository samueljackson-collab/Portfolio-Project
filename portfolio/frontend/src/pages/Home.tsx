import { useEffect, useState } from 'react'
import api from '../lib/api'

type HealthState = 'loading' | 'ok' | 'down'

function Home() {
  const [health, setHealth] = useState<HealthState>('loading')
  const [message, setMessage] = useState('Checking API…')

  useEffect(() => {
    api
      .get('/health')
      .then((response) => {
        setHealth(response.data.status === 'ok' ? 'ok' : 'down')
        setMessage('FastAPI backend is reachable.')
      })
      .catch(() => {
        setHealth('down')
        setMessage('Unable to reach FastAPI backend. Start with `make dev`.')
      })
  }, [])

  const statusStyles: Record<HealthState, string> = {
    loading: 'bg-yellow-500/30 text-yellow-200',
    ok: 'bg-emerald-500/30 text-emerald-200',
    down: 'bg-rose-500/30 text-rose-200'
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Operational Snapshot</h2>
        <p className="text-sm text-slate-400">
          This frontend pings the FastAPI backend and reports status.
        </p>
      </div>
      <div className={`rounded-lg border border-slate-700 p-4 ${statusStyles[health]}`}>
        <h3 className="text-lg font-medium">API Health</h3>
        <p>{message}</p>
      </div>
      <div className="rounded-lg border border-slate-800 bg-slate-800/60 p-4">
        <h3 className="text-lg font-medium">Next Steps</h3>
        <ol className="list-decimal space-y-2 pl-5 text-sm text-slate-300">
          <li>Register a user via the UI once forms are implemented.</li>
          <li>Use API tokens to create content entries from the CLI or frontend.</li>
          <li>Review dashboards under <code>docs/observability</code>.</li>
        </ol>
      </div>
    </section>
  )
}

export default Home
