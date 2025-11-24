import React, { useEffect, useState } from 'react'
import { roamingApi, type RoamingAgreements, type RoamingSession } from '../api'
import { RoamingAgreementsCard } from '../components/roaming/RoamingAgreementsCard'
import { RoamingSessionPanel } from '../components/roaming/RoamingSessionPanel'

export const RoamingConsole: React.FC = () => {
  const [agreements, setAgreements] = useState<RoamingAgreements>({})
  const [session, setSession] = useState<RoamingSession | undefined>(undefined)
  const [form, setForm] = useState({ imsi: '', home_network: '310-410', visited_network: '208-01' })
  const [eventType, setEventType] = useState('location_update')
  const [eventMessage, setEventMessage] = useState('Location update accepted')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    roamingApi.listAgreements().then(setAgreements)
  }, [])

  const handleSessionCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const created = await roamingApi.createSession({ ...form, roaming_enabled: true })
      setSession(created)
    } finally {
      setLoading(false)
    }
  }

  const handleEvent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!session) return
    setLoading(true)
    try {
      const updated = await roamingApi.addEvent(session.session_id, {
        type: eventType,
        message: eventMessage,
      })
      setSession(updated)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-start gap-6">
        <form onSubmit={handleSessionCreate} className="bg-white shadow rounded-lg p-4 w-1/2 space-y-3">
          <h2 className="text-xl font-semibold text-gray-800">Initiate Roaming</h2>
          <label className="block text-sm">
            IMSI
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={form.imsi}
              onChange={e => setForm({ ...form, imsi: e.target.value })}
              required
            />
          </label>
          <label className="block text-sm">
            Home network (MCC-MNC)
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={form.home_network}
              onChange={e => setForm({ ...form, home_network: e.target.value })}
              required
            />
          </label>
          <label className="block text-sm">
            Visited network (MCC-MNC)
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={form.visited_network}
              onChange={e => setForm({ ...form, visited_network: e.target.value })}
              required
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? 'Creating session...' : 'Start roaming session'}
          </button>
        </form>
        <div className="w-1/2">
          <RoamingAgreementsCard agreements={agreements} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <RoamingSessionPanel session={session} />
        </div>
        <form onSubmit={handleEvent} className="bg-white shadow rounded-lg p-4 space-y-3">
          <h3 className="text-lg font-semibold text-gray-800">Drive state machine</h3>
          <p className="text-sm text-gray-500">Send synthetic events to test attach and roam flows.</p>
          <label className="block text-sm">
            Event type
            <select
              className="mt-1 w-full border rounded px-3 py-2"
              value={eventType}
              onChange={e => setEventType(e.target.value)}
              disabled={!session}
            >
              <option value="authenticate">Authenticate</option>
              <option value="location_update">Location update</option>
              <option value="activate_roaming">Activate roaming</option>
              <option value="detach">Detach</option>
            </select>
          </label>
          <label className="block text-sm">
            Message
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={eventMessage}
              onChange={e => setEventMessage(e.target.value)}
              disabled={!session}
            />
          </label>
          <button
            type="submit"
            disabled={!session || loading}
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-60"
          >
            {loading ? 'Sending event...' : 'Send event'}
          </button>
        </form>
      </div>
    </div>
  )
}

