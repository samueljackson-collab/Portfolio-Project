import React from 'react'
import type { RoamingAgreements } from '../../api'

interface Props {
  agreements: RoamingAgreements
}

export const RoamingAgreementsCard: React.FC<Props> = ({ agreements }) => (
  <div className="bg-white shadow rounded-lg p-4">
    <div className="flex items-center justify-between">
      <h3 className="text-lg font-semibold text-gray-800">Roaming Agreements</h3>
      <span className="text-sm text-gray-500">Home → Partners</span>
    </div>
    <div className="mt-4 space-y-2">
      {Object.entries(agreements).map(([home, partners]) => (
        <div key={home} className="border border-gray-100 rounded p-2">
          <div className="text-sm font-medium text-gray-700">{home}</div>
          <div className="text-xs text-gray-500">{partners.join(', ') || 'None'}</div>
        </div>
      ))}
      {Object.keys(agreements).length === 0 && (
        <p className="text-sm text-gray-500">No roaming agreements configured.</p>
      )}
    </div>
  </div>
)

