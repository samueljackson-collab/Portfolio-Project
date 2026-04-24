import { useEffect, useRef, useState } from 'react'
import type { BugFinding } from '../api/types'

interface SSEPayload {
  status: string
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  risk_score: number
  new_findings: BugFinding[]
  error?: string
}

export interface FeedResult {
  status: string
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  risk_score: number
  findings: BugFinding[]
}

interface Props {
  scanId: string
  filename: string
  platform: string
  onComplete: (result: FeedResult) => void
}

const SEV_TEXT: Record<string, string> = {
  Critical: 'text-red-400',
  High:     'text-orange-400',
  Medium:   'text-yellow-400',
  Low:      'text-green-400',
}

const SEV_BORDER: Record<string, string> = {
  Critical: 'border-red-500/30 bg-red-500/5',
  High:     'border-orange-500/30 bg-orange-500/5',
  Medium:   'border-yellow-500/30 bg-yellow-500/5',
  Low:      'border-green-500/30 bg-green-500/5',
}

export function LiveScanFeed({ scanId, filename, platform, onComplete }: Props) {
  const [findings, setFindings] = useState<BugFinding[]>([])
  const [counts, setCounts] = useState({ critical: 0, high: 0, medium: 0, low: 0 })
  const [riskScore, setRiskScore] = useState(0)
  const [status, setStatus] = useState<string>('running')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const feedRef = useRef<HTMLDivElement>(null)
  const allFindingsRef = useRef<BugFinding[]>([])
  const finalDataRef = useRef<Omit<FeedResult, 'findings'> | null>(null)

  useEffect(() => {
    const es = new EventSource(`/api/scans/${scanId}/events`)

    es.onmessage = (event) => {
      try {
        const payload: SSEPayload = JSON.parse(event.data)

        setCounts({
          critical: payload.critical_count,
          high:     payload.high_count,
          medium:   payload.medium_count,
          low:      payload.low_count,
        })
        setRiskScore(payload.risk_score)
        setStatus(payload.status)

        if (payload.new_findings?.length) {
          allFindingsRef.current = [...allFindingsRef.current, ...payload.new_findings]
          setFindings(prev => [...prev, ...payload.new_findings])
        }

        if (payload.status === 'complete' || payload.status === 'failed') {
          finalDataRef.current = {
            status:         payload.status,
            critical_count: payload.critical_count,
            high_count:     payload.high_count,
            medium_count:   payload.medium_count,
            low_count:      payload.low_count,
            risk_score:     payload.risk_score,
          }
          es.close()
        }
      } catch { /* ignore parse errors */ }
    }

    es.onerror = () => es.close()

    return () => es.close()
  }, [scanId])

  // Auto-scroll feed to latest finding
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight
    }
  }, [findings])

  // After completion, brief pause then hand off results
  useEffect(() => {
    if ((status === 'complete' || status === 'failed') && finalDataRef.current) {
      const t = setTimeout(() => {
        onComplete({ ...finalDataRef.current!, findings: allFindingsRef.current })
      }, 1500)
      return () => clearTimeout(t)
    }
  }, [status, onComplete])

  const total = counts.critical + counts.high + counts.medium + counts.low

  return (
    <div className="bg-gray-950 rounded-xl border border-gray-800 overflow-hidden font-mono text-sm animate-fade-in">
      {/* Terminal title bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          <span className="text-gray-400 text-xs truncate">
            <span className="text-emerald-400">[ SCANNING ]</span>{' '}
            {filename || 'unnamed'} — platform: {platform.toUpperCase()}
          </span>
        </div>
        <StatusIndicator status={status} />
      </div>

      {/* Severity counters */}
      <div className="grid grid-cols-4 divide-x divide-gray-800 border-b border-gray-800">
        <Counter label="CRITICAL" value={counts.critical} color="text-red-400"    />
        <Counter label="HIGH"     value={counts.high}     color="text-orange-400" />
        <Counter label="MEDIUM"   value={counts.medium}   color="text-yellow-400" />
        <Counter label="LOW"      value={counts.low}      color="text-green-400"  />
      </div>

      {/* Live feed */}
      <div
        ref={feedRef}
        className="h-80 overflow-y-auto p-3 space-y-1.5"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#374151 transparent' }}
      >
        {findings.length === 0 && (
          <div className="flex items-center gap-2 text-gray-600 py-2">
            <span className="animate-blink text-emerald-500">█</span>
            <span>Initializing ruleset analysis…</span>
          </div>
        )}

        {findings.map((f, i) => (
          <FindingEntry
            key={f.id}
            finding={f}
            index={i}
            expanded={expandedId === f.id}
            onToggle={() => setExpandedId(expandedId === f.id ? null : f.id)}
          />
        ))}

        {status === 'running' && findings.length > 0 && (
          <div className="flex items-center gap-2 text-gray-700 text-xs pt-1">
            <span className="animate-blink text-emerald-500">█</span>
            <span>Analyzing…</span>
          </div>
        )}

        {(status === 'complete' || status === 'failed') && (
          <div className={`mt-2 pt-2 border-t border-gray-800 text-center text-xs tracking-wider ${status === 'complete' ? 'text-emerald-400' : 'text-red-400'}`}>
            {status === 'complete'
              ? `✓ SCAN COMPLETE — ${total} finding${total !== 1 ? 's' : ''} · Risk Score: ${riskScore.toFixed(0)}/100`
              : '✗ SCAN FAILED — check backend logs'}
          </div>
        )}
      </div>

      {/* Risk score bar */}
      <div className="px-4 py-2.5 border-t border-gray-800 bg-gray-900/50">
        <div className="flex items-center justify-between text-xs text-gray-600 mb-1.5">
          <span>RISK SCORE</span>
          <span className={riskScore >= 70 ? 'text-red-400' : riskScore >= 40 ? 'text-orange-400' : 'text-emerald-400'}>
            {riskScore.toFixed(0)}/100
          </span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded overflow-hidden">
          <div
            className={`h-full rounded transition-all duration-500 ${
              riskScore >= 70 ? 'bg-red-500' : riskScore >= 40 ? 'bg-orange-400' : 'bg-emerald-400'
            }`}
            style={{ width: `${Math.min(riskScore, 100)}%` }}
          />
        </div>
      </div>
    </div>
  )
}

function StatusIndicator({ status }: { status: string }) {
  if (status === 'running' || status === 'pending')
    return (
      <span className="flex items-center gap-1.5 text-xs text-yellow-400">
        <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
        LIVE
      </span>
    )
  if (status === 'complete')
    return (
      <span className="flex items-center gap-1.5 text-xs text-emerald-400">
        <span className="w-2 h-2 rounded-full bg-emerald-400" />
        DONE
      </span>
    )
  return (
    <span className="flex items-center gap-1.5 text-xs text-red-400">
      <span className="w-2 h-2 rounded-full bg-red-400" />
      ERROR
    </span>
  )
}

function Counter({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="py-2 px-3 text-center">
      <div className={`text-2xl font-bold tabular-nums transition-all duration-300 ${color}`}>{value}</div>
      <div className="text-xs text-gray-600 mt-0.5">{label}</div>
    </div>
  )
}

function FindingEntry({
  finding, index, expanded, onToggle,
}: {
  finding: BugFinding
  index: number
  expanded: boolean
  onToggle: () => void
}) {
  const textColor  = SEV_TEXT[finding.severity]   ?? 'text-gray-400'
  const borderColor = SEV_BORDER[finding.severity] ?? 'border-gray-700'

  return (
    <div
      className={`border rounded px-3 py-2 cursor-pointer transition-all animate-slide-in-left ${borderColor}`}
      style={{ animationDelay: `${Math.min(index * 0.04, 0.5)}s` }}
      onClick={onToggle}
    >
      <div className="flex items-center gap-2 min-w-0">
        <span className={`font-bold uppercase text-xs shrink-0 ${textColor}`}>
          [{finding.severity}]
        </span>
        <span className="text-gray-300 flex-1 truncate">{finding.title}</span>
        {finding.line_number != null && (
          <span className="text-gray-600 text-xs shrink-0">L{finding.line_number}</span>
        )}
        <span className="text-gray-600 text-xs shrink-0">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="mt-2.5 space-y-2 text-xs animate-fade-in">
          <p className="text-gray-400 leading-relaxed">{finding.description}</p>
          {finding.code_snippet && (
            <pre className="rounded bg-black/50 px-3 py-2 text-emerald-300 overflow-x-auto leading-relaxed whitespace-pre text-xs">
              {finding.code_snippet}
            </pre>
          )}
          <p className="text-gray-500 italic leading-relaxed">{finding.recommendation}</p>
          {(finding.cwe_id || finding.cvss_score != null) && (
            <div className="flex gap-4 text-gray-600">
              {finding.cwe_id && <span className="text-blue-400/70">{finding.cwe_id}</span>}
              {finding.cvss_score != null && <span>CVSS {finding.cvss_score}</span>}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
