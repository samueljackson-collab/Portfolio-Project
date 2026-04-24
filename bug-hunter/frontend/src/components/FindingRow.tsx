import { useState } from 'react'
import type { BugFinding } from '../api/types'
import { SeverityBadge } from './SeverityBadge'

interface Props {
  finding: BugFinding
  index: number
}

export function FindingRow({ finding, index }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <>
      <tr
        className="hover:bg-gray-50 cursor-pointer transition-colors"
        onClick={() => setExpanded(e => !e)}
      >
        <td className="px-4 py-3 text-xs text-gray-400 font-mono w-10">{index}</td>
        <td className="px-4 py-3 font-medium text-gray-900 text-sm max-w-xs">
          <div className="truncate">{finding.title}</div>
        </td>
        <td className="px-4 py-3 w-28">
          <SeverityBadge severity={finding.severity} size="sm" />
        </td>
        <td className="px-4 py-3 text-xs text-gray-600 w-28">{finding.category}</td>
        <td className="px-4 py-3 text-xs font-mono text-purple-600 w-24">
          {finding.cwe_id ?? '—'}
        </td>
        <td className="px-4 py-3 text-xs font-semibold w-16">
          {finding.cvss_score != null ? (
            <span className={finding.cvss_score >= 9 ? 'text-red-600' : finding.cvss_score >= 7 ? 'text-orange-500' : 'text-yellow-600'}>
              {finding.cvss_score.toFixed(1)}
            </span>
          ) : '—'}
        </td>
        <td className="px-4 py-3 text-xs text-gray-400 font-mono w-14">
          {finding.line_number ?? '—'}
        </td>
        <td className="px-4 py-3 w-8 text-gray-400">
          <svg className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </td>
      </tr>
      {expanded && (
        <tr className="bg-slate-50">
          <td colSpan={8} className="px-6 py-5 border-t border-slate-100">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-2">Description</div>
                <p className="text-sm text-slate-700 leading-relaxed">{finding.description}</p>

                <div className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-2 mt-4">Evidence</div>
                <p className="text-xs font-mono text-slate-600 bg-white border border-slate-200 rounded p-2 break-words">
                  {finding.evidence}
                </p>
              </div>
              <div>
                {finding.code_snippet && (
                  <>
                    <div className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-2">
                      Code (Line {finding.line_number ?? '?'})
                    </div>
                    <pre className="text-xs bg-slate-900 text-slate-200 rounded-lg p-3 overflow-x-auto font-mono leading-relaxed mb-4 whitespace-pre-wrap break-words">
                      {finding.code_snippet}
                    </pre>
                  </>
                )}
                <div className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-2">Recommendation</div>
                <p className="text-sm text-slate-700 leading-relaxed">{finding.recommendation}</p>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  )
}
