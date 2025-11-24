import React from 'react'
import type { RoamingSession } from '../../api'

interface Props {
  session?: RoamingSession
}

export const RoamingSessionPanel: React.FC<Props> = ({ session }) => {
  if (!session) {
    return (
      <div className="bg-white shadow rounded-lg p-4 text-gray-600">
        Initiate a roaming session to view live telemetry.
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Session {session.session_id}</h3>
          <p className="text-sm text-gray-500">IMSI {session.imsi}</p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 capitalize">
          {session.state}
        </span>
      </div>
      <dl className="grid grid-cols-2 gap-4 text-sm text-gray-700">
        <div>
          <dt className="font-medium">Home Network</dt>
          <dd>{session.home_network}</dd>
        </div>
        <div>
          <dt className="font-medium">Visited Network</dt>
          <dd>{session.visited_network}</dd>
        </div>
      </dl>
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Event history</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {session.events.map((event, idx) => (
            <div key={idx} className="border border-gray-100 rounded p-2 text-sm text-gray-700">
              <div className="flex items-center justify-between">
                <span className="font-medium capitalize">{event.type}</span>
                <span className="text-xs text-gray-500">{new Date(event.timestamp).toLocaleString()}</span>
              </div>
              <p className="text-gray-600 text-sm">{event.message}</p>
            </div>
          ))}
          {session.events.length === 0 && <p className="text-gray-500 text-sm">No events yet.</p>}
        </div>
      </div>
    </div>
  )
}

