import { useEffect, useState, useMemo } from 'react'

interface Props {
  onDone: () => void
}

const TITLE = 'BUG HUNTER'
const SUBTITLE = 'CROSS-PLATFORM VULNERABILITY SCANNER v2.0'

export function LoadingScreen({ onDone }: Props) {
  const [titleLen, setTitleLen] = useState(0)
  const [subLen, setSubLen] = useState(0)
  const [phase, setPhase] = useState<'title' | 'sub' | 'bar' | 'out'>('title')
  const [exiting, setExiting] = useState(false)

  // Type the title
  useEffect(() => {
    if (phase !== 'title') return
    if (titleLen >= TITLE.length) { setPhase('sub'); return }
    const t = setTimeout(() => setTitleLen(n => n + 1), 80)
    return () => clearTimeout(t)
  }, [titleLen, phase])

  // Type the subtitle
  useEffect(() => {
    if (phase !== 'sub') return
    if (subLen >= SUBTITLE.length) { setPhase('bar'); return }
    const t = setTimeout(() => setSubLen(n => n + 1), 28)
    return () => clearTimeout(t)
  }, [subLen, phase])

  // Brief pause on bar phase then exit
  useEffect(() => {
    if (phase !== 'bar') return
    const t = setTimeout(() => {
      setExiting(true)
      setTimeout(onDone, 650)
    }, 700)
    return () => clearTimeout(t)
  }, [phase, onDone])

  // Random hex particles — stable across renders
  const particles = useMemo(() =>
    Array.from({ length: 48 }, (_, i) => ({
      id: i,
      char: Math.random().toString(16).slice(2, 4).toUpperCase(),
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      dur: `${2.5 + Math.random() * 3}s`,
      delay: `${Math.random() * 4}s`,
      size: Math.random() > 0.7 ? 'text-sm' : 'text-xs',
    })), [])

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden ${exiting ? 'animate-fade-out-screen' : 'animate-fade-in'}`}
      style={{ backgroundColor: '#020817' }}
    >
      {/* Hex particle rain */}
      <div className="absolute inset-0 pointer-events-none select-none">
        {particles.map(p => (
          <span
            key={p.id}
            className={`absolute font-mono text-green-500/25 animate-hex-drift ${p.size}`}
            style={{ left: p.left, top: p.top, '--dur': p.dur, '--delay': p.delay } as React.CSSProperties}
          >
            {p.char}
          </span>
        ))}
      </div>

      {/* Scan line */}
      <div
        className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-red-500/50 to-transparent pointer-events-none animate-scan-line"
      />

      {/* Main content */}
      <div className="relative z-10 text-center space-y-5 px-6">
        {/* Bug icon */}
        <div className="flex justify-center mb-2">
          <svg className="w-14 h-14 text-red-500 animate-pulse-glow" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20 8h-2.81a5.985 5.985 0 0 0-1.82-1.96L17 4.41 15.59 3l-2.17 2.17a6.002 6.002 0 0 0-2.84 0L8.41 3 7 4.41l1.62 1.63C7.88 6.55 7.26 7.22 6.81 8H4v2h2.09c-.05.33-.09.66-.09 1v1H4v2h2v1c0 .34.04.67.09 1H4v2h2.81c1.04 1.79 2.97 3 5.19 3s4.15-1.21 5.19-3H20v-2h-2.09c.05-.33.09-.66.09-1v-1h2v-2h-2v-1c0-.34-.04-.67-.09-1H20V8zm-6 8h-4v-2h4v2zm0-4h-4v-2h4v2z"/>
          </svg>
        </div>

        {/* Title typewriter */}
        <h1
          className="text-6xl sm:text-8xl font-black font-mono tracking-wider text-red-500 animate-pulse-glow"
        >
          {TITLE.slice(0, titleLen)}
          {phase === 'title' && <span className="animate-blink opacity-100">█</span>}
        </h1>

        {/* Subtitle typewriter */}
        <p className="text-sm sm:text-base font-mono text-emerald-400 tracking-widest min-h-[1.5rem]">
          {SUBTITLE.slice(0, subLen)}
          {phase === 'sub' && <span className="animate-blink">█</span>}
        </p>

        {/* Loading bar */}
        {phase === 'bar' && (
          <div className="mt-6 space-y-2 animate-fade-in">
            <p className="text-xs font-mono text-gray-500 tracking-widest">
              INITIALIZING ANALYSIS ENGINE
            </p>
            <div className="w-72 mx-auto h-1 rounded bg-gray-800 overflow-hidden">
              <div className="h-full bg-red-500 rounded animate-loading-bar" />
            </div>
          </div>
        )}
      </div>

      {/* Corner decorations */}
      <div className="absolute top-4 left-4 text-xs font-mono text-gray-700 select-none">
        SYS://VULN-SCAN-ENGINE
      </div>
      <div className="absolute bottom-4 right-4 text-xs font-mono text-gray-700 select-none">
        {new Date().getFullYear()} · READY
      </div>
    </div>
  )
}
