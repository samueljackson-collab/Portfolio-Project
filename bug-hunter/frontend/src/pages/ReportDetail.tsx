import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { reportsApi } from '../api/client'
import type { Report } from '../api/types'
import { riskScoreBg } from '../components/SeverityBadge'

export function ReportDetail() {
  const { id } = useParams<{ id: string }>()
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    reportsApi.get(id).then(setReport).finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center text-gray-400 text-sm animate-pulse">
      Loading report...
    </div>
  )

  if (!report) return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center text-red-500 text-sm">
      Report not found. <Link to="/reports" className="underline">Back to reports</Link>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to="/reports" className="hover:underline">Reports</Link>
        <span>/</span>
        <span className="font-mono text-gray-700">{report.id.slice(0, 8)}...</span>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Bug Hunt Report</h1>
            <div className="text-xs text-gray-400 mt-1 space-x-4">
              <span>Report ID: <span className="font-mono">{report.id}</span></span>
              <span>Generated: {new Date(report.generated_at).toLocaleString()}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-sm font-bold px-3 py-1 rounded-lg ${riskScoreBg(report.risk_score)}`}>
              Risk: {report.risk_score.toFixed(0)}/100
            </span>
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
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
          <div className="text-xs font-bold uppercase tracking-wider text-blue-500 mb-2">Executive Summary</div>
          <p className="text-sm text-blue-900 leading-relaxed">{report.executive_summary}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex items-center">
          <div className="text-center w-full">
            <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1">Total Findings</div>
            <div className={`text-5xl font-extrabold ${riskScoreBg(report.risk_score)} inline-block px-6 py-3 rounded-xl`}>
              {report.total_findings}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">Full Report</h2>
          <p className="text-xs text-gray-400 mt-0.5">Rendered inline — use Export buttons above for download</p>
        </div>
        <div
          className="p-6"
          dangerouslySetInnerHTML={{ __html: report.html_content ?? '' }}
          style={{ maxWidth: '100%', overflow: 'auto' }}
        />
      </div>
    </div>
  )
}
