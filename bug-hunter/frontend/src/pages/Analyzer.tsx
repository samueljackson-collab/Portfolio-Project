import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { scansApi } from '../api/client'
import type { Platform, ScanSession, BugFinding } from '../api/types'
import { PlatformTabBar, PLATFORMS } from '../components/PlatformTab'
import { FindingRow } from '../components/FindingRow'
import { LiveScanFeed, type FeedResult } from '../components/LiveScanFeed'

const PLATFORM_EXTENSIONS: Record<Platform, string> = {
  android: '.java, .kt, .xml',
  ios: '.swift, .m, .mm',
  windows: '.cs, .cpp, .c, .cxx, .ps1',
  macos: '.swift, .m, .mm, .sh, .bash',
  web: '.js, .ts, .jsx, .tsx, .py, .php, .html, .rb',
}

const PLATFORM_PLACEHOLDERS: Record<Platform, string> = {
  android: `// Paste Android (Java/Kotlin) code here\n// Example:\npublic void login(String userId) {\n    String query = "SELECT * FROM users WHERE id = " + userId;\n    db.rawQuery(query, null);\n    Log.d("Auth", "Password: " + password);\n}`,
  ios: `// Paste iOS (Swift/Objective-C) code here\n// Example:\nlet token = UserDefaults.standard.string(forKey: "auth_token")\nlet url = URL(string: apiEndpoint)!\nURLSession.shared.dataTask(with: url).resume()`,
  windows: `// Paste Windows (C#/C++/PowerShell) code here\n// Example:\nvoid ProcessInput(char* userInput) {\n    char buffer[64];\n    strcpy(buffer, userInput); // unsafe!\n}`,
  macos: `// Paste macOS (Swift/ObjC/Bash) code here\n// Example:\nlet task = Process()\ntask.launchPath = "/bin/sh"\ntask.arguments = ["-c", userInput]`,
  web: `// Paste Web code here (JS, Python, PHP, etc.)\n// Example:\napp.get('/search', (req, res) => {\n  const query = "SELECT * FROM items WHERE name = '" + req.query.q + "'";\n  db.query(query);\n});`,
}

type TabState = {
  code: string
  filename: string
  scanId: string | null
  scanData: ScanSession | null
  showFeed: boolean
  error: string | null
}

function makeFreshState(): TabState {
  return { code: '', filename: '', scanId: null, scanData: null, showFeed: false, error: null }
}

function FilterBar({
  search, setSearch,
  severity, setSeverity,
  category, setCategory,
  categories,
  total, filtered,
}: {
  search: string; setSearch: (s: string) => void
  severity: string; setSeverity: (s: string) => void
  category: string; setCategory: (s: string) => void
  categories: string[]
  total: number; filtered: number
}) {
  return (
    <div className="flex flex-wrap gap-3 items-center mb-4">
      <input
        type="search"
        placeholder="Search findings..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm flex-1 min-w-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        value={severity}
        onChange={e => setSeverity(e.target.value)}
        className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Severities</option>
        {['Critical', 'High', 'Medium', 'Low'].map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <select
        value={category}
        onChange={e => setCategory(e.target.value)}
        className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Categories</option>
        {categories.map(c => <option key={c} value={c}>{c}</option>)}
      </select>
      <span className="text-xs text-gray-400">Showing {filtered} of {total}</span>
    </div>
  )
}

export function Analyzer() {
  const navigate = useNavigate()
  const [activePlatform, setActivePlatform] = useState<Platform>('android')
  const [tabStates, setTabStates] = useState<Record<Platform, TabState>>(
    () => Object.fromEntries(PLATFORMS.map(p => [p, makeFreshState()])) as Record<Platform, TabState>
  )
  const [submitting, setSubmitting] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  const [search, setSearch] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('')
  const [filterCategory, setFilterCategory] = useState('')

  const state = tabStates[activePlatform]

  const updateState = useCallback((platform: Platform, patch: Partial<TabState>) => {
    setTabStates(prev => ({ ...prev, [platform]: { ...prev[platform], ...patch } }))
  }, [])

  useEffect(() => {
    setSearch('')
    setFilterSeverity('')
    setFilterCategory('')
  }, [activePlatform])

  const handleSubmit = async () => {
    const { code, filename } = state
    if (!code.trim()) {
      updateState(activePlatform, { error: 'Please paste or upload code to analyze.' })
      return
    }
    setSubmitting(true)
    updateState(activePlatform, { error: null, scanId: null, scanData: null, showFeed: false })
    try {
      const session = await scansApi.create({
        platform: activePlatform,
        filename: filename || `unnamed.${activePlatform}`,
        code_content: code,
      })
      updateState(activePlatform, { scanId: session.id, scanData: session, showFeed: true })
    } catch {
      updateState(activePlatform, { error: 'Failed to start scan. Is the backend running?' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleFeedComplete = useCallback((result: FeedResult) => {
    setTabStates(prev => {
      const cur = prev[activePlatform]
      return {
        ...prev,
        [activePlatform]: {
          ...cur,
          showFeed: false,
          scanData: cur.scanData
            ? {
                ...cur.scanData,
                status:         result.status as ScanSession['status'],
                critical_count: result.critical_count,
                high_count:     result.high_count,
                medium_count:   result.medium_count,
                low_count:      result.low_count,
                risk_score:     result.risk_score,
                findings:       result.findings,
              }
            : cur.scanData,
        },
      }
    })
  }, [activePlatform])

  const handleFile = (file: File) => {
    const reader = new FileReader()
    reader.onload = e => {
      updateState(activePlatform, { code: e.target?.result as string, filename: file.name })
    }
    reader.readAsText(file)
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [activePlatform])

  const findings: BugFinding[] = state.scanData?.findings ?? []
  const categories = [...new Set(findings.map(f => f.category))].sort()

  const filtered = findings.filter(f => {
    if (filterSeverity && f.severity !== filterSeverity) return false
    if (filterCategory && f.category !== filterCategory) return false
    if (search) {
      const q = search.toLowerCase()
      return (
        f.title.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q) ||
        f.category.toLowerCase().includes(q)
      )
    }
    return true
  })

  const isScanning = state.showFeed ||
    state.scanData?.status === 'running' ||
    state.scanData?.status === 'pending'

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900">Code Analyzer</h1>
        <p className="text-gray-500 text-sm mt-1">Select a platform, paste code or upload a file, then run the scanner.</p>
      </div>

      {/* Input panel — fades while scanning */}
      <div
        className={`bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden transition-opacity duration-300 ${isScanning ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}
      >
        <PlatformTabBar active={activePlatform} onChange={p => setActivePlatform(p)} />

        <div className="p-6 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Filename</label>
              <input
                type="text"
                placeholder="e.g. MainActivity.java"
                value={state.filename}
                onChange={e => updateState(activePlatform, { filename: e.target.value })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Upload File</label>
              <label className="cursor-pointer inline-flex items-center gap-2 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Choose File
                <input
                  type="file"
                  className="hidden"
                  accept={PLATFORM_EXTENSIONS[activePlatform]}
                  onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
                />
              </label>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">
              Code ({PLATFORM_EXTENSIONS[activePlatform]})
            </label>
            <div
              className={`relative border-2 rounded-lg transition-colors ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200'}`}
              onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
            >
              <textarea
                value={state.code}
                onChange={e => updateState(activePlatform, { code: e.target.value })}
                placeholder={PLATFORM_PLACEHOLDERS[activePlatform]}
                rows={14}
                className="w-full px-4 py-3 font-mono text-sm resize-y focus:outline-none rounded-lg bg-transparent"
                spellCheck={false}
              />
              {isDragging && (
                <div className="absolute inset-0 flex items-center justify-center bg-blue-50/80 rounded-lg pointer-events-none">
                  <span className="text-blue-600 font-semibold">Drop file here</span>
                </div>
              )}
            </div>
          </div>

          {state.error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2">
              {state.error}
            </p>
          )}

          <div className="flex justify-between items-center">
            {state.scanData?.status === 'complete' && (
              <button
                onClick={() => navigate(`/scan/${state.scanId}`)}
                className="text-sm text-blue-600 hover:underline"
              >
                View full scan →
              </button>
            )}
            <div className="ml-auto">
              <button
                onClick={handleSubmit}
                disabled={submitting || isScanning}
                className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-6 py-2 rounded-lg text-sm transition-colors"
              >
                {submitting ? 'Submitting…' : 'Run Scan'}
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Live terminal feed — shown while scan is running via SSE */}
      {state.showFeed && state.scanId && (
        <LiveScanFeed
          scanId={state.scanId}
          filename={state.filename || 'unnamed'}
          platform={activePlatform}
          onComplete={handleFeedComplete}
        />
      )}

      {/* Results panel — appears after feed completes */}
      {state.scanData?.status === 'complete' && !state.showFeed && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden animate-fade-in">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-4">
              <h2 className="font-bold text-gray-900">Scan Results</h2>
              <div className="flex gap-2 text-xs">
                {(state.scanData.critical_count ?? 0) > 0 && (
                  <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded font-bold">
                    {state.scanData.critical_count} Critical
                  </span>
                )}
                {(state.scanData.high_count ?? 0) > 0 && (
                  <span className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded font-semibold">
                    {state.scanData.high_count} High
                  </span>
                )}
                {(state.scanData.medium_count ?? 0) > 0 && (
                  <span className="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
                    {state.scanData.medium_count} Medium
                  </span>
                )}
                {(state.scanData.low_count ?? 0) > 0 && (
                  <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded">
                    {state.scanData.low_count} Low
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">
                Risk Score:{' '}
                <strong
                  className={
                    (state.scanData.risk_score ?? 0) >= 70
                      ? 'text-red-600'
                      : (state.scanData.risk_score ?? 0) >= 40
                      ? 'text-orange-500'
                      : 'text-green-600'
                  }
                >
                  {(state.scanData.risk_score ?? 0).toFixed(0)}/100
                </strong>
              </span>
              <button
                onClick={() => navigate(`/scan/${state.scanId}`)}
                className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 font-semibold"
              >
                Full Report
              </button>
            </div>
          </div>

          <div className="p-5">
            {findings.length === 0 ? (
              <p className="text-center text-green-600 py-6 font-medium">
                No vulnerabilities detected in this scan.
              </p>
            ) : (
              <>
                <FilterBar
                  search={search} setSearch={setSearch}
                  severity={filterSeverity} setSeverity={setFilterSeverity}
                  category={filterCategory} setCategory={setFilterCategory}
                  categories={categories}
                  total={findings.length} filtered={filtered.length}
                />
                {filtered.length === 0 ? (
                  <p className="text-center text-gray-400 py-6 text-sm">
                    No findings match your filters.
                  </p>
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
                        {filtered.map((f, i) => (
                          <FindingRow key={f.id} finding={f} index={i + 1} />
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {state.scanData?.status === 'failed' && !state.showFeed && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700 text-sm">
          Scan failed. Please try again or check the backend logs.
        </div>
      )}
    </div>
  )
}
