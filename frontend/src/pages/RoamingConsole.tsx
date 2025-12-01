import React, { useEffect, useState } from 'react'
import { roamingService, RoamingSessionList, RoamingSession } from '../api'
import { RoamingSessionTable } from '../components'

const initialPayload = {
  imsi: '310410999999999',
  home_network: '310-410',
  visited_network: '208-01',
}

const RoamingConsole: React.FC = () => {
  const [form, setForm] = useState(initialPayload)
  const [sessions, setSessions] = useState<RoamingSession[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshSessions = async () => {
    const payload: RoamingSessionList = await roamingService.listSessions()
    setSessions(payload.sessions)
  }

  useEffect(() => {
    refreshSessions()
  }, [])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const created = await roamingService.createSession(form)
      await roamingService.authenticate(created.session_id)
      await roamingService.activate(created.session_id)
      await refreshSessions()
    } catch (err) {
      setError('Failed to create roaming session. Check agreements or API connectivity.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Roaming Ops Console</h1>
        <p className="text-gray-600">Simulate dual-region roaming onboarding and activation.</p>
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700">IMSI</label>
            <input
              className="mt-1 w-full rounded border-gray-300 shadow-sm"
              value={form.imsi}
              onChange={(e) => setForm({ ...form, imsi: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Home PLMN</label>
            <input
              className="mt-1 w-full rounded border-gray-300 shadow-sm"
              value={form.home_network}
              onChange={(e) => setForm({ ...form, home_network: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Visited PLMN</label>
            <input
              className="mt-1 w-full rounded border-gray-300 shadow-sm"
              value={form.visited_network}
              onChange={(e) => setForm({ ...form, visited_network: e.target.value })}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white py-2 px-4 rounded shadow hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Provisioning…' : 'Start Session'}
          </button>
        </form>
        {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
      </div>

      <RoamingSessionTable sessions={sessions} />
    </div>
  )
}

export default RoamingConsole
