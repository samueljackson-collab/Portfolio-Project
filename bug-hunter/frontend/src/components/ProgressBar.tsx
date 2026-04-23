interface Props {
  label?: string
  animated?: boolean
}

export function ProgressBar({ label = 'Scanning...', animated = true }: Props) {
  return (
    <div className="space-y-2">
      {label && <p className="text-sm text-gray-600 font-medium">{label}</p>}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-blue-500 ${animated ? 'animate-pulse' : ''}`}
          style={{ width: animated ? '100%' : '100%' }}
        />
      </div>
    </div>
  )
}
