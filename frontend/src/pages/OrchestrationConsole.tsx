import React, { useEffect, useMemo, useState } from 'react'
import { orchestrationService } from '../api/services'
import type { OrchestrationRun, OrchestrationSummary } from '../api/types'

const statusColors: Record<OrchestrationRun['status'], string> = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  succeeded: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-yellow-100 text-yellow-800',
}

const environments = ['dev', 'staging', 'production']

export const OrchestrationConsole: React.FC = () => {
  const [runs, setRuns] = useState<OrchestrationRun[]>([])
  const [summary, setSummary] = useState<OrchestrationSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({
    name: 'deploy-portfolio',
    environment: 'staging',
    target_version: 'v1.0.0',
    kickoff_notes: 'rolling out orchestrator-enabled stack',
  })

  const sortedRuns = useMemo(
    () => runs.slice().sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime()),
    [runs]
  )

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [runsResponse, summaryResponse] = await Promise.all([
        orchestrationService.listRuns(),
        orchestrationService.getSummary(),
      ])
      setRuns(runsResponse)
      setSummary(summaryResponse)
    } catch (err) {
      setError('Unable to reach orchestration API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      await orchestrationService.createRun(form)
      await loadData()
    } catch (err) {
      setError('Failed to start orchestration run')
    }
  }

  const renderStatusPill = (status: OrchestrationRun['status']) => (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColors[status]}`}>
      {status}
    </span>
  )

  return (
    <div className="max-w-6xl mx-auto py-10 px-4">
      <header className="mb-8">
        <p className="text-sm uppercase tracking-wide text-gray-500">Operations</p>
        <h1 className="text-3xl font-bold text-gray-900">Orchestration Console</h1>
        <p className="text-gray-600 mt-2">
          Track deployment runs, push status events, and monitor the fleet in real time.
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {error && <div className="md:col-span-3 text-red-600 text-sm">{error}</div>}
        {summary &&
          Object.entries(summary).map(([status, count]) => (
            <div key={status} className="bg-white shadow rounded-lg p-4">
              <p className="text-sm text-gray-500 capitalize">{status}</p>
              <p className="text-3xl font-bold text-gray-900">{count}</p>
            </div>
          ))}
        {!summary && <div className="text-gray-500">No runs yet</div>}
      </section>

      <section className="bg-white shadow rounded-lg p-6 mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Start a new run</h2>
          {loading && <span className="text-sm text-blue-600">Refreshing…</span>}
        </div>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Run name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Environment</label>
            <select
              value={form.environment}
              onChange={(e) => setForm({ ...form, environment: e.target.value })}
              className="input"
            >
              {environments.map((env) => (
                <option key={env} value={env}>
                  {env}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Target version</label>
            <input
              type="text"
              value={form.target_version}
              onChange={(e) => setForm({ ...form, target_version: e.target.value })}
              className="input"
              required
            />
          </div>
          <div className="md:col-span-4">
            <label className="block text-sm font-medium text-gray-700">Kickoff notes</label>
            <textarea
              value={form.kickoff_notes}
              onChange={(e) => setForm({ ...form, kickoff_notes: e.target.value })}
              className="input"
              rows={2}
            />
          </div>
          <div className="md:col-span-4 flex justify-end">
            <button type="submit" className="btn-primary">
              Start run
            </button>
          </div>
        </form>
      </section>

      <section className="space-y-4">
        {sortedRuns.map((run) => (
          <div key={run.id} className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-500">{run.environment} • {run.target_version}</p>
                <h3 className="text-lg font-semibold text-gray-900">{run.name}</h3>
                <p className="text-sm text-gray-500">
                  Started {new Date(run.started_at).toLocaleString()} • Updated {new Date(run.updated_at).toLocaleString()}
                </p>
              </div>
              {renderStatusPill(run.status)}
            </div>
            <div className="mt-4 border-t border-gray-100 pt-4 space-y-2">
              {run.steps.map((step) => (
                <div key={step.timestamp} className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-2" />
                  <div>
                    <p className="text-sm text-gray-900">{step.message}</p>
                    <p className="text-xs text-gray-500">{new Date(step.timestamp).toLocaleString()} • {step.level}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        {sortedRuns.length === 0 && (
          <div className="bg-white shadow rounded-lg p-6 text-gray-500">No orchestration runs yet. Kick off the first deployment above.</div>
        )}
      </section>
    </div>
  )
}

export default OrchestrationConsole
