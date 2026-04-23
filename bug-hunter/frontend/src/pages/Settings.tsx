import { useEffect, useState } from 'react'
import { healthApi } from '../api/client'

const RULE_CATEGORIES = ['Security', 'Memory', 'Performance', 'Logic', 'Crypto', 'Network', 'Crash']

function useLocalStorage<T>(key: string, defaultValue: T): [T, (v: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key)
      return stored ? JSON.parse(stored) : defaultValue
    } catch {
      return defaultValue
    }
  })

  const set = (v: T) => {
    setValue(v)
    localStorage.setItem(key, JSON.stringify(v))
  }

  return [value, set]
}

export function Settings() {
  const [enabledCategories, setEnabledCategories] = useLocalStorage<Record<string, boolean>>(
    'bh_rule_categories',
    Object.fromEntries(RULE_CATEGORIES.map(c => [c, true]))
  )
  const [cvssMin, setCvssMin] = useLocalStorage<number>('bh_cvss_min', 0)
  const [includeSnippets, setIncludeSnippets] = useLocalStorage<boolean>('bh_include_snippets', true)
  const [summaryVerbosity, setSummaryVerbosity] = useLocalStorage<'brief' | 'detailed'>('bh_summary_verbosity', 'detailed')

  const [apiStatus, setApiStatus] = useState<'checking' | 'ok' | 'error'>('checking')
  const [apiVersion, setApiVersion] = useState('')

  useEffect(() => {
    healthApi.check()
      .then(d => { setApiStatus('ok'); setApiVersion(d.version) })
      .catch(() => setApiStatus('error'))
  }, [])

  const toggleCategory = (cat: string) => {
    setEnabledCategories({ ...enabledCategories, [cat]: !enabledCategories[cat] })
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Configure scanner rules, report preferences, and view app status.</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4">
        <h2 className="text-base font-bold text-gray-900">Scanner Rule Categories</h2>
        <p className="text-sm text-gray-500">Toggle categories to include or exclude in future scans.</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {RULE_CATEGORIES.map(cat => (
            <label key={cat} className="flex items-center gap-2.5 cursor-pointer group">
              <div
                onClick={() => toggleCategory(cat)}
                className={`w-9 h-5 rounded-full relative transition-colors cursor-pointer ${
                  enabledCategories[cat] ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              >
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                  enabledCategories[cat] ? 'translate-x-4' : 'translate-x-0.5'
                }`} />
              </div>
              <span className={`text-sm font-medium ${enabledCategories[cat] ? 'text-gray-800' : 'text-gray-400'}`}>
                {cat}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-5">
        <h2 className="text-base font-bold text-gray-900">Severity Threshold</h2>
        <div>
          <label className="text-sm text-gray-700 font-medium">
            Minimum CVSS Score to Report: <span className="font-bold text-blue-600">{cvssMin.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min={0}
            max={10}
            step={0.5}
            value={cvssMin}
            onChange={e => setCvssMin(parseFloat(e.target.value))}
            className="w-full mt-2 accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0 (All)</span>
            <span>5 (Medium+)</span>
            <span>7 (High+)</span>
            <span>10 (Critical only)</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-5">
        <h2 className="text-base font-bold text-gray-900">Report Options</h2>

        <label className="flex items-center gap-3 cursor-pointer">
          <div
            onClick={() => setIncludeSnippets(!includeSnippets)}
            className={`w-9 h-5 rounded-full relative transition-colors cursor-pointer ${includeSnippets ? 'bg-blue-600' : 'bg-gray-300'}`}
          >
            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${includeSnippets ? 'translate-x-4' : 'translate-x-0.5'}`} />
          </div>
          <div>
            <span className="text-sm font-medium text-gray-800">Include code snippets in reports</span>
            <p className="text-xs text-gray-400">Shows the offending code excerpt for each finding</p>
          </div>
        </label>

        <div>
          <label className="block text-sm font-medium text-gray-800 mb-2">Executive Summary Verbosity</label>
          <div className="flex gap-3">
            {(['brief', 'detailed'] as const).map(v => (
              <label key={v} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="verbosity"
                  value={v}
                  checked={summaryVerbosity === v}
                  onChange={() => setSummaryVerbosity(v)}
                  className="accent-blue-600"
                />
                <span className="text-sm text-gray-700 capitalize">{v}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-3">
        <h2 className="text-base font-bold text-gray-900">App Info</h2>
        <div className="flex items-center gap-3">
          <div className={`w-2.5 h-2.5 rounded-full ${apiStatus === 'ok' ? 'bg-green-500' : apiStatus === 'error' ? 'bg-red-500' : 'bg-yellow-400 animate-pulse'}`} />
          <span className="text-sm text-gray-700">
            API: {apiStatus === 'ok' ? `Connected (v${apiVersion})` : apiStatus === 'error' ? 'Offline — backend not reachable' : 'Checking...'}
          </span>
        </div>
        <div className="text-xs text-gray-400 space-y-1">
          <div>Frontend: Bug Hunter v1.0.0</div>
          <div>Platforms supported: Android, iOS, Windows, macOS, Web</div>
          <div>Rule engine: Pattern-based static analysis + AST heuristics</div>
        </div>
      </div>
    </div>
  )
}
