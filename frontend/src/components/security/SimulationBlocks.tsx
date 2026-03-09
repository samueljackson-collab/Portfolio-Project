/**
 * SimulationBlocks — a collection of pure display components used by the
 * Security Simulators page.
 *
 * DESIGN PRINCIPLE:
 * These components are intentionally "dumb" — they receive typed data from the
 * parent page and render it. They have no internal state, no API calls, and no
 * side effects. This keeps them easy to test and reuse in different contexts.
 *
 * All types are imported from the shared API types file so the component props
 * stay in sync with the backend schema automatically.
 */

import React from 'react'
import {
  AnalysisReport,
  DeploymentSummary,
  DetectionRule,
  Endpoint,
  Hypothesis,
  IncidentEvent,
  OperationEvent,
  SocAlert
} from '../../api'

/**
 * badgeColors — maps severity strings to Tailwind colour classes.
 *
 * Using a lookup object instead of a switch/ternary chain makes it trivial to
 * add new severity levels (e.g. 'critical') without touching the render logic.
 * The fallback `'bg-gray-100'` in the consuming component handles unknown values.
 */
const badgeColors: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700'
}

/**
 * RedTeamTimeline — renders the day-by-day event log for a red team operation.
 *
 * Each event shows:
 * - Which simulated day it occurred on
 * - The category (e.g. "recon", "lateral movement", "exfiltration")
 * - A short description of what the actor did
 * - A badge showing whether the blue team detected the activity
 *
 * The "Detected / Covert" badge uses red/green to make detection status
 * immediately clear at a glance — important for demo readability.
 */
export const RedTeamTimeline: React.FC<{ events: OperationEvent[] }> = ({ events }) => (
  <div className="space-y-3">
    {events.map((event) => (
      <div
        key={event.id}
        className="border rounded-md p-3 flex items-center justify-between bg-white shadow-sm"
      >
        <div>
          <p className="text-sm text-gray-500">Day {event.day}</p>
          <p className="font-semibold">{event.category}</p>
          <p className="text-gray-600 text-sm">{event.description}</p>
        </div>
        <span
          className={`text-xs px-3 py-1 rounded-full ${
            event.detected ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
          }`}
        >
          {event.detected ? 'Detected' : 'Covert'}
        </span>
      </div>
    ))}
  </div>
)

/**
 * RansomwareTimeline — renders the ordered list of lifecycle events for a
 * ransomware incident simulation.
 *
 * Uses an ordered list (`<ol>`) to convey that the events are sequential
 * milestones (e.g. "Infection" → "Encryption" → "Ransom demand" → "Recovery").
 * The numbered list makes the progression visually obvious without needing
 * timestamps.
 */
export const RansomwareTimeline: React.FC<{ events: IncidentEvent[] }> = ({ events }) => (
  <ol className="list-decimal list-inside space-y-1 text-sm">
    {events.map((event) => (
      <li key={event.id} className="text-gray-800">
        <span className="font-semibold">{event.type}</span> — {event.details}
      </li>
    ))}
  </ol>
)

/**
 * SocAlertTable — renders the SOC alert queue in a sortable-looking table.
 *
 * Columns: Title, Severity (colour-coded badge), Status.
 *
 * Severity badges use the `badgeColors` lookup defined at the top of this file.
 * Unknown severity values fall back to a neutral grey badge so the UI never
 * crashes on unexpected API data.
 */
export const SocAlertTable: React.FC<{ alerts: SocAlert[] }> = ({ alerts }) => (
  <div className="overflow-x-auto">
    <table className="min-w-full text-sm">
      <thead>
        <tr className="text-left text-gray-500">
          <th className="p-2">Title</th>
          <th className="p-2">Severity</th>
          <th className="p-2">Status</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert) => (
          <tr key={alert.id} className="border-t">
            <td className="p-2">{alert.title}</td>
            <td className="p-2">
              <span className={`px-2 py-1 rounded-full text-xs ${badgeColors[alert.severity] || 'bg-gray-100'}`}>
                {alert.severity}
              </span>
            </td>
            <td className="p-2 text-gray-700">{alert.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)

/**
 * HuntingBoard — side-by-side view of threat hunting hypotheses and the
 * detection rules that were promoted from their findings.
 *
 * WHY TWO COLUMNS:
 * This layout directly mirrors the analyst workflow: hypotheses live on the
 * left, and when a finding is validated and promoted it "moves" to become a
 * detection rule on the right. The visual separation makes the pipeline clear.
 */
export const HuntingBoard: React.FC<{
  hypotheses: Hypothesis[]
  rules: DetectionRule[]
}> = ({ hypotheses, rules }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div className="border rounded-md p-4 bg-white shadow-sm">
      <h4 className="font-semibold mb-2">Hypotheses</h4>
      <ul className="space-y-1 text-sm text-gray-700">
        {hypotheses.map((hyp) => (
          <li key={hyp.id}>
            <span className="font-semibold">{hyp.title}</span> — {hyp.status}
          </li>
        ))}
      </ul>
    </div>
    <div className="border rounded-md p-4 bg-white shadow-sm">
      <h4 className="font-semibold mb-2">Detection Rules</h4>
      <ul className="space-y-1 text-sm text-gray-700">
        {rules.map((rule) => (
          <li key={rule.id}>
            <span className="font-semibold">{rule.name}</span> — {rule.status}
          </li>
        ))}
      </ul>
    </div>
  </div>
)

/**
 * MalwareReportCard — displays the result of a simulated malware analysis.
 *
 * Shows three sections:
 * 1. Static Analysis — file-level indicators (imports, strings, entropy score)
 * 2. Dynamic Analysis — runtime behaviour (network calls, file system writes)
 * 3. YARA Rule — the generated detection rule in monospace for readability
 *
 * The `<pre>` tag for the YARA rule preserves whitespace and indentation,
 * which is important for YARA rule syntax legibility.
 *
 * Returns null-ish message when no report exists yet (before "Upload Sample"
 * has been clicked) rather than crashing on undefined data.
 */
export const MalwareReportCard: React.FC<{ report?: AnalysisReport | null }> = ({ report }) => {
  if (!report) {
    return <p className="text-sm text-gray-600">No analysis generated yet.</p>
  }

  return (
    <div className="border rounded-md p-4 bg-white shadow-sm space-y-2">
      <div>
        <h4 className="font-semibold">Static Analysis</h4>
        <p className="text-sm text-gray-700">{report.static_analysis}</p>
      </div>
      <div>
        <h4 className="font-semibold">Dynamic Analysis</h4>
        <p className="text-sm text-gray-700">{report.dynamic_analysis}</p>
      </div>
      <div>
        <h4 className="font-semibold">YARA Rule</h4>
        <pre className="bg-gray-100 text-xs p-2 rounded-md overflow-x-auto">{report.yara_rule}</pre>
      </div>
    </div>
  )
}

/**
 * EdrEndpointTable — lists registered endpoints with their agent version and
 * online status.
 *
 * isOutdated() — INTENTIONAL DEMO BEHAVIOUR:
 * Any agent on major version 1.x (e.g. '1.0.0', '1.9.3') is flagged as
 * outdated and shown in red. The Security Simulators page registers new
 * endpoints with `agent_version: '1.0.0'`, so every newly registered endpoint
 * immediately appears outdated. This is by design — it demonstrates the EDR
 * "agent upgrade" workflow to portfolio reviewers without requiring manual setup.
 *
 * If the minimum supported version changes, update the `< 2` threshold here
 * to match the new baseline.
 */
export const EdrEndpointTable: React.FC<{ endpoints: Endpoint[] }> = ({ endpoints }) => {
  /**
   * Returns true if the agent version's major number is below the minimum
   * supported major version (currently 2). Agents on v1.x are intentionally
   * registered as outdated in the demo to showcase the upgrade workflow.
   */
  const isOutdated = (version: string) => {
    const [major] = version.split('.')
    // Major version < 2 = outdated (demo threshold — all 1.x agents need upgrade)
    return Number(major) < 2
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500">
            <th className="p-2">Hostname</th>
            <th className="p-2">Agent</th>
            <th className="p-2">Online</th>
          </tr>
        </thead>
        <tbody>
          {endpoints.map((endpoint) => (
            <tr key={endpoint.id} className="border-t">
              <td className="p-2">{endpoint.hostname}</td>
              <td className="p-2">
                <span className={isOutdated(endpoint.agent_version) ? 'text-red-700 font-semibold' : ''}>
                  {endpoint.agent_version}
                </span>
              </td>
              <td className="p-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs ${
                    endpoint.online ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {endpoint.online ? 'Online' : 'Offline'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * DeploymentSummaryCard — 2×2 metric grid showing high-level EDR coverage.
 *
 * Metrics:
 * - Total: count of all registered endpoints
 * - Online: count of endpoints currently reporting in
 * - Outdated: count of endpoints running an old agent version
 * - Coverage: percentage of registered endpoints that are online
 *
 * Returns null (renders nothing) when `summary` is falsy, which happens before
 * the first `deploymentSummary()` API call completes.
 */
export const DeploymentSummaryCard: React.FC<{ summary?: DeploymentSummary | null }> = ({ summary }) => {
  if (!summary) return null

  return (
    <div className="grid grid-cols-2 gap-3 text-sm">
      <div className="p-3 bg-white rounded shadow-sm">
        <p className="text-gray-500">Total</p>
        <p className="font-bold text-lg">{summary.total_endpoints}</p>
      </div>
      <div className="p-3 bg-white rounded shadow-sm">
        <p className="text-gray-500">Online</p>
        <p className="font-bold text-lg">{summary.online}</p>
      </div>
      <div className="p-3 bg-white rounded shadow-sm">
        <p className="text-gray-500">Outdated</p>
        <p className="font-bold text-lg">{summary.outdated_agents}</p>
      </div>
      <div className="p-3 bg-white rounded shadow-sm">
        <p className="text-gray-500">Coverage</p>
        <p className="font-bold text-lg">{summary.coverage}%</p>
      </div>
    </div>
  )
}
