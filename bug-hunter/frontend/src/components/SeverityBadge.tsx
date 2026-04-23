import type { Severity } from '../api/types'

const CONFIG: Record<Severity, { bg: string; text: string; dot: string }> = {
  Critical: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
  High:     { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500' },
  Medium:   { bg: 'bg-yellow-100', text: 'text-yellow-700', dot: 'bg-yellow-400' },
  Low:      { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
}

interface Props {
  severity: Severity
  size?: 'sm' | 'md'
}

export function SeverityBadge({ severity, size = 'md' }: Props) {
  const c = CONFIG[severity]
  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold ${px} ${c.bg} ${c.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {severity}
    </span>
  )
}

export function riskScoreClass(score: number): string {
  if (score >= 70) return 'text-red-600'
  if (score >= 40) return 'text-orange-500'
  if (score >= 20) return 'text-yellow-500'
  return 'text-green-600'
}

export function riskScoreBg(score: number): string {
  if (score >= 70) return 'bg-red-100 text-red-700'
  if (score >= 40) return 'bg-orange-100 text-orange-700'
  if (score >= 20) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}
