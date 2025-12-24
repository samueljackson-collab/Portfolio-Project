import React from 'react'
import {
  AnalysisReport,
  DeploymentSummary,
  DetectionRule,
  Endpoint,
  Hypothesis,
  IncidentEvent,
  MalwareDetail,
  OperationEvent,
  SocAlert
} from '../../api'

const badgeColors: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700'
}

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

export const RansomwareTimeline: React.FC<{ events: IncidentEvent[] }> = ({ events }) => (
  <ol className="list-decimal list-inside space-y-1 text-sm">
    {events.map((event) => (
      <li key={event.id} className="text-gray-800">
        <span className="font-semibold">{event.type}</span> — {event.details}
      </li>
    ))}
  </ol>
)

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

export const EdrEndpointTable: React.FC<{ endpoints: Endpoint[] }> = ({ endpoints }) => {
  const isOutdated = (version: string) => {
    const [major] = version.split('.')
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

