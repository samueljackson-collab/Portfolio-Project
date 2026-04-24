import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { scansApi, reportsApi } from '../api/client'
import type { ScanSession, Report, BugFinding } from '../api/types'
import { SeverityBadge, riskScoreBg } from '../components/SeverityBadge'
import { PlatformBadge } from '../components/PlatformTab'
import { FindingRow } from '../components/FindingRow'
import { ProgressBar } from '../components/ProgressBar'

export function ScanDetail() {
  const { id } = useParams<{ id: string }>()
  const [scan, setScan] = useState<ScanSession | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('')
  const [filterCategory, setFilterCategory] = useState('')

  useEffect(() => {
    if (!id) return
    let interval: ReturnType<typeof setInterval>

    const fetchScan = async () => {
      const data = await scansApi.get(id)
      setScan(data)
      setLoading(false)
      if (data.status === 'complete' || data.status === 'failed') {
        clearInterval(interval)
        if (data.status === 'complete') {
          const reports = await reportsApi.list()
          const r = reports.find(rep => rep.session_id === id)
          if (r) setReport(r)
        }
      }
    }

    fetchScan()
    interval = setInterval(fetchScan, 2000)
    return () => clearInterval(interval)
  }, [id])

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center text-gray-400 text-sm animate-pulse">
      Loading scan...
    </div>
  )

  if (!scan) return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center text-red-500 text-sm">
      Scan not found. <Link to="/" className="underline">Back to dashboard</Link>
    </div>
  )

  const findings: BugFinding[] = scan.findings ?? []
  const categories = [...new Set(findings.map(f => f.category))].sort()
  const filtered = findings.filter(f => {
    if (filterSeverity && f.severity !== filterSeverity) return false
    if (filterCategory && f.category !== filterCategory) return false
    if (search) {
      const q = search.toLowerCase()
      return f.title.toLowerCase().includes(q) || f.description.toLowerCase().includes(q)
    }
    return true
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to="/" className="hover:underline">Dashboard</Link>
        <span>/</span>
        <span className="text-gray-700 font-medium truncate">{scan.filename}</span>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <PlatformBadge platform={scan.platform} />
              <h1 className="text-xl font-bold text-gray-900 font-mono">{scan.filename}</h1>
              <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{scan.language}</span>
            </div>
            <div className="text-xs text-gray-400 space-x-4">
              <span>Scan ID: <span className="font-mono">{scan.id}</span></span>
              <span>Started: {new Date(scan.created_at).toLocaleString()}</span>
              {scan.completed_at && <span>Completed: {new Date(scan.completed_at).toLocaleString()}</span>}
            </div>
          </div>

          {scan.status === 'complete' && (
            <div className="flex items-center gap-3">
              {report && (
                <>
                  <a
                    href={reportsApi.htmlUrl(report.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs border border-gray-200 text-gray-600 hover:bg-gray-50 px-3 py-1.5 rounded-lg font-medium transition-colors"
                  >
                    Export HTML
                  </a>
                  <a
                    href={reportsApi.pdfUrl(report.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs bg-slate-900 text-white hover:bg-slate-800 px-3 py-1.5 rounded-lg font-medium transition-colors"
                  >
                    Export PDF
                  </a>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {(scan.status === 'pending' || scan.status === 'running') && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
          <ProgressBar label={`Running ${scan.platform} analysis on ${scan.filename}...`} />
        </div>
      )}

      {scan.status === 'complete' && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
              { label: 'Critical', val: scan.critical_count, color: 'text-red-600' },
              { label: 'High', val: scan.high_count, color: 'text-orange-500' },
              { label: 'Medium', val: scan.medium_count, color: 'text-yellow-500' },
              { label: 'Low', val: scan.low_count, color: 'text-green-600' },
              { label: 'Risk Score', val: `${scan.risk_score.toFixed(0)}/100`, color: scan.risk_score >= 70 ? 'text-red-600' : scan.risk_score >= 40 ? 'text-orange-500' : 'text-green-600' },
            ].map(item => (
              <div key={item.label} className="bg-white rounded-xl border border-gray-200 p-4 text-center shadow-sm">
                <div className="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">{item.label}</div>
                <div className={`text-2xl font-extrabold ${item.color}`}>{item.val}</div>
              </div>
            ))}
          </div>

          {report && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
              <div className="text-xs font-bold uppercase tracking-wider text-blue-500 mb-2">Executive Summary</div>
              <p className="text-sm text-blue-900 leading-relaxed">{report.executive_summary}</p>
            </div>
          )}

          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100">
              <h2 className="font-bold text-gray-900">Findings ({findings.length})</h2>
            </div>
            <div className="p-5">
              {findings.length === 0 ? (
                <p className="text-center text-green-600 py-6 font-medium">No vulnerabilities detected.</p>
              ) : (
                <>
                  <div className="flex flex-wrap gap-3 mb-4">
                    <input
                      type="search"
                      placeholder="Search findings..."
                      value={search}
                      onChange={e => setSearch(e.target.value)}
                      className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm flex-1 min-w-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <select value={filterSeverity} onChange={e => setFilterSeverity(e.target.value)} className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="">All Severities</option>
                      {['Critical', 'High', 'Medium', 'Low'].map(s => <option key={s}>{s}</option>)}
                    </select>
                    <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)} className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="">All Categories</option>
                      {categories.map(c => <option key={c}>{c}</option>)}
                    </select>
                    <span className="text-xs text-gray-400 self-center">Showing {filtered.length} of {findings.length}</span>
                  </div>
                  {filtered.length === 0 ? (
                    <p className="text-center text-gray-400 py-6 text-sm">No findings match your filters.</p>
                  ) : (
                    <div className="overflow-x-auto rounded-lg border border-gray-100">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          <tr>
                            <th className="px-4 py-2.5 text-left w-10">#</th>
                            <th className="px-4 py-2.5 text-left">Title</th>
                            <th className="px-4 py-2.5 text-left w-28">Severity</th>
                            <th className="px-4 py-2.5 text-left w-28">Category</th>
                            <th className="px-4 py-2.5 text-left w-24">CWE</th>
                            <th className="px-4 py-2.5 text-left w-16">CVSS</th>
                            <th className="px-4 py-2.5 text-left w-14">Line</th>
                            <th className="px-4 py-2.5 w-8"></th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {filtered.map((f, i) => <FindingRow key={f.id} finding={f} index={i + 1} />)}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </>
      )}

      {scan.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700 text-sm">
          This scan encountered an error. Please try submitting the code again.
        </div>
      )}
    </div>
  )
}
