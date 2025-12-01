import React from 'react'
import type { RoamingSession } from '../../api'

interface Props {
  sessions: RoamingSession[]
}

const stateBadge: Record<RoamingSession['state'], string> = {
  idle: 'bg-gray-200 text-gray-800',
  attached: 'bg-blue-100 text-blue-800',
  authenticated: 'bg-green-100 text-green-800',
  active: 'bg-emerald-100 text-emerald-800',
  detached: 'bg-amber-100 text-amber-800',
}

export const RoamingSessionTable: React.FC<Props> = ({ sessions }) => {
  return (
    <div className="overflow-x-auto rounded-lg shadow bg-white">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IMSI</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Home</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Visited</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">State</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Events</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {sessions.map((session) => (
            <tr key={session.session_id}>
              <td className="px-4 py-3 text-sm font-mono text-gray-800">{session.imsi}</td>
              <td className="px-4 py-3 text-sm text-gray-800">{session.home_network}</td>
              <td className="px-4 py-3 text-sm text-gray-800">{session.visited_network}</td>
              <td className="px-4 py-3 text-sm">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${stateBadge[session.state]}`}>
                  {session.state}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{new Date(session.last_updated).toLocaleString()}</td>
              <td className="px-4 py-3 text-xs text-gray-600 max-w-xs truncate" title={session.events.join('\n')}>
                {session.events[session.events.length - 1] || 'Pending action'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
