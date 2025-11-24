import React, { useEffect, useState } from 'react'
import { operationsService } from '../api'
import type { DeploymentDashboardResponse, DeploymentRecord, RegionRollup } from '../api/types'

const RegionCard: React.FC<{ rollup: RegionRollup }> = ({ rollup }) => (
  <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
    <div className="flex items-center justify-between">
      <h3 className="text-lg font-semibold text-gray-800">{rollup.region}</h3>
      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${rollup.healthy === rollup.services ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
        {rollup.healthy}/{rollup.services} healthy
      </span>
    </div>
    <p className="mt-2 text-sm text-gray-600">Desired replicas: {rollup.desired_replicas}</p>
    <p className="text-sm text-gray-600">Available replicas: {rollup.available_replicas}</p>
  </div>
)

const OperatorConsole: React.FC = () => {
  const [dashboard, setDashboard] = useState<DeploymentDashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await operationsService.getDashboard()
        setDashboard(data)
      } catch (err) {
        setError('Unable to load deployment telemetry')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <header className="mb-6">
        <p className="text-sm uppercase tracking-wide text-indigo-600">Operations</p>
        <h1 className="text-3xl font-bold text-gray-900">Multi-region operator console</h1>
        <p className="mt-2 text-gray-600">
          Live view of deployment posture, release status, and regional health aligned with the GitOps topology.
        </p>
      </header>

      {loading && <p className="text-gray-500">Loading deployment metrics...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {dashboard && (
        <>
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {dashboard.regions.map((rollup) => (
              <RegionCard key={rollup.region} rollup={rollup} />
            ))}
          </section>

          <section className="mt-8 rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="border-b px-4 py-3">
              <h2 className="text-lg font-semibold text-gray-800">Latest releases</h2>
              <p className="text-sm text-gray-600">Auditable record of the ten most recent rollouts</p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Service</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Region</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Cluster</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Version</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Replicas</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {dashboard.latest_releases.map((deployment: DeploymentRecord) => (
                    <tr key={deployment.id}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">{deployment.service_name}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">{deployment.region}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">{deployment.cluster}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">{deployment.version}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm">
                        <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${deployment.status === 'Healthy' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
                          {deployment.status}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                        {deployment.available_replicas}/{deployment.desired_replicas}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  )
}

export default OperatorConsole
