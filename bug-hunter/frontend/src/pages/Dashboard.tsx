import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { scansApi } from '../api/client'
import type { ScanSession } from '../api/types'
import { SeverityBadge, riskScoreBg } from '../components/SeverityBadge'
import { PlatformBadge } from '../components/PlatformTab'

function StatCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">{label}</div>
      <div className={`text-3xl font-extrabold ${color}`}>{value}</div>
    </div>
  )
}

function StatusPill({ status }: { status: string }) {
  const cls =
    status === 'complete' ? 'bg-green-100 text-green-700' :
    status === 'running' || status === 'pending' ? 'bg-blue-100 text-blue-700 animate-pulse' :
    'bg-red-100 text-red-700'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${cls}`}>
      {status}
    </span>
  )
}

export function Dashboard() {
  const [scans, setScans] = useState<ScanSession[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    scansApi.list({ limit: 20 }).then(setScans).finally(() => setLoading(false))
  }, [])

  const totalFindings = scans.reduce((s, sc) => s + sc.critical_count + sc.high_count + sc.medium_count + sc.low_count, 0)
  const totalCritical = scans.reduce((s, sc) => s + sc.critical_count, 0)
  const avgRisk = scans.length
    ? Math.round(scans.reduce((s, sc) => s + sc.risk_score, 0) / scans.length)
    : 0

  const maxFindings = Math.max(1, ...scans.map(sc => sc.critical_count + sc.high_count + sc.medium_count + sc.low_count))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Cross-platform vulnerability scanner overview</p>
        </div>
        <button
          onClick={() => navigate('/analyze')}
          className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New Scan
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Total Scans" value={scans.length} color="text-slate-800" />
        <StatCard label="Total Findings" value={totalFindings} color="text-slate-700" />
        <StatCard label="Critical Issues" value={totalCritical} color="text-red-600" />
        <StatCard label="Avg Risk Score" value={`${avgRisk}/100`} color={avgRisk >= 70 ? 'text-red-600' : avgRisk >= 40 ? 'text-orange-500' : 'text-green-600'} />
      </div>

      {scans.filter(s => s.status === 'complete').length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h2 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wider">Findings by Severity (Recent Scans)</h2>
          <div className="space-y-3">
            {[
              { label: 'Critical', key: 'critical_count', color: 'bg-red-500' },
              { label: 'High', key: 'high_count', color: 'bg-orange-500' },
              { label: 'Medium', key: 'medium_count', color: 'bg-yellow-400' },
              { label: 'Low', key: 'low_count', color: 'bg-green-500' },
            ].map(({ label, key, color }) => {
              const total = scans.reduce((s, sc) => s + (sc[key as keyof ScanSession] as number), 0)
              const pct = Math.round((total / Math.max(1, totalFindings)) * 100)
              return (
                <div key={label} className="flex items-center gap-3">
                  <span className="text-xs font-semibold w-16 text-gray-600">{label}</span>
                  <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-xs font-bold text-gray-700 w-6 text-right">{total}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-bold text-gray-900">Recent Scans</h2>
          <Link to="/reports" className="text-xs text-blue-600 hover:underline">View all reports →</Link>
        </div>

        {loading ? (
          <div className="p-10 text-center text-gray-400 text-sm animate-pulse">Loading scans...</div>
        ) : scans.length === 0 ? (
          <div className="p-10 text-center">
            <p className="text-gray-400 text-sm mb-3">No scans yet. Submit your first code scan to get started.</p>
            <button onClick={() => navigate('/analyze')} className="text-blue-600 text-sm font-medium hover:underline">
              Start a scan →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3 text-left">Platform</th>
                  <th className="px-5 py-3 text-left">File</th>
                  <th className="px-5 py-3 text-left">Status</th>
                  <th className="px-5 py-3 text-left">Findings</th>
                  <th className="px-5 py-3 text-left">Risk</th>
                  <th className="px-5 py-3 text-left">Date</th>
                  <th className="px-5 py-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {scans.map(scan => {
                  const total = scan.critical_count + scan.high_count + scan.medium_count + scan.low_count
                  return (
                    <tr key={scan.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3">
                        <PlatformBadge platform={scan.platform} />
                      </td>
                      <td className="px-5 py-3 text-sm text-gray-700 max-w-xs">
                        <div className="truncate font-mono text-xs">{scan.filename}</div>
                        <div className="text-xs text-gray-400">{scan.language}</div>
                      </td>
                      <td className="px-5 py-3"><StatusPill status={scan.status} /></td>
                      <td className="px-5 py-3">
                        {scan.status === 'complete' ? (
                          <div className="flex items-center gap-1 text-xs">
                            {scan.critical_count > 0 && <span className="text-red-600 font-bold">{scan.critical_count}C</span>}
                            {scan.high_count > 0 && <span className="text-orange-500 font-semibold">{scan.high_count}H</span>}
                            {scan.medium_count > 0 && <span className="text-yellow-600">{scan.medium_count}M</span>}
                            {scan.low_count > 0 && <span className="text-green-600">{scan.low_count}L</span>}
                            {total === 0 && <span className="text-gray-400">None</span>}
                          </div>
                        ) : <span className="text-gray-300 text-xs">—</span>}
                      </td>
                      <td className="px-5 py-3">
                        {scan.status === 'complete' ? (
                          <span className={`text-xs font-bold px-2 py-0.5 rounded ${riskScoreBg(scan.risk_score)}`}>
                            {scan.risk_score.toFixed(0)}
                          </span>
                        ) : <span className="text-gray-300 text-xs">—</span>}
                      </td>
                      <td className="px-5 py-3 text-xs text-gray-400">
                        {new Date(scan.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-3">
                        <Link
                          to={`/scan/${scan.id}`}
                          className="text-xs text-blue-600 hover:underline font-medium"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
