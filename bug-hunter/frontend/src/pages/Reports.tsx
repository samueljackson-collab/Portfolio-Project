import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { reportsApi } from '../api/client'
import type { Report } from '../api/types'
import { riskScoreBg } from '../components/SeverityBadge'

export function Reports() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    reportsApi.list({ limit: 100 }).then(setReports).finally(() => setLoading(false))
  }, [])

  const filtered = reports.filter(r => {
    if (search) {
      return r.executive_summary.toLowerCase().includes(search.toLowerCase()) ||
        r.session_id.toLowerCase().includes(search.toLowerCase())
    }
    return true
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900">Reports</h1>
        <p className="text-gray-500 text-sm mt-1">All generated bug hunt reports with detailed findings.</p>
      </div>

      <div className="flex gap-3">
        <input
          type="search"
          placeholder="Search reports..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-gray-400 text-sm animate-pulse">Loading reports...</div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center">
            <p className="text-gray-400 text-sm mb-3">
              {reports.length === 0 ? 'No reports yet. Complete a scan to generate your first report.' : 'No reports match your search.'}
            </p>
            {reports.length === 0 && (
              <Link to="/analyze" className="text-blue-600 text-sm font-medium hover:underline">
                Start a scan →
              </Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3 text-left">Report ID</th>
                  <th className="px-5 py-3 text-left">Summary</th>
                  <th className="px-5 py-3 text-left">Findings</th>
                  <th className="px-5 py-3 text-left">Risk Score</th>
                  <th className="px-5 py-3 text-left">Generated</th>
                  <th className="px-5 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(report => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-4 text-xs font-mono text-gray-400">
                      {report.id.slice(0, 8)}...
                    </td>
                    <td className="px-5 py-4 max-w-sm">
                      <p className="text-sm text-gray-700 line-clamp-2">{report.executive_summary}</p>
                    </td>
                    <td className="px-5 py-4 text-sm font-semibold text-gray-700">
                      {report.total_findings}
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${riskScoreBg(report.risk_score)}`}>
                        {report.risk_score.toFixed(0)}/100
                      </span>
                    </td>
                    <td className="px-5 py-4 text-xs text-gray-400">
                      {new Date(report.generated_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/report/${report.id}`}
                          className="text-xs text-blue-600 hover:underline font-medium"
                        >
                          View
                        </Link>
                        <a
                          href={reportsApi.htmlUrl(report.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-gray-500 hover:underline"
                        >
                          HTML
                        </a>
                        <a
                          href={reportsApi.pdfUrl(report.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-gray-500 hover:underline"
                        >
                          PDF
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
