import React, { useEffect, useMemo, useState } from 'react'
import { orchestrationService } from '../api/services'
import type { OrchestrationPlan, OrchestrationRun } from '../api/types'

const statusStyles: Record<OrchestrationRun['status'], string> = {
  running: 'bg-amber-100 text-amber-800 border-amber-200',
  succeeded: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  failed: 'bg-rose-100 text-rose-800 border-rose-200'
}

export const OrchestrationConsole: React.FC = () => {
  const [plans, setPlans] = useState<OrchestrationPlan[]>([])
  const [runs, setRuns] = useState<OrchestrationRun[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<string>('')
  const [changeTicket, setChangeTicket] = useState('')
  const [windowLabel, setWindowLabel] = useState('standard')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const latestRun = useMemo(() => runs[0], [runs])

  const loadData = async () => {
    try {
      const [plansResponse, runsResponse] = await Promise.all([
        orchestrationService.listPlans(),
        orchestrationService.listRuns()
      ])
      setPlans(plansResponse)
      setRuns(runsResponse)
      if (!selectedPlanId && plansResponse.length > 0) {
        setSelectedPlanId(plansResponse[0].id)
      }
    } catch (err) {
      console.error(err)
      setError('Unable to load orchestration data. Please retry.')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const triggerRun = async () => {
    if (!selectedPlanId) return
    setLoading(true)
    setError(null)
    try {
      const result = await orchestrationService.startRun({
        plan_id: selectedPlanId,
        parameters: {
          change_ticket: changeTicket,
          change_window: windowLabel
        }
      })
      setRuns((prev) => [result, ...prev])
      setSuccess(`Run ${result.id} completed with status ${result.status}`)
      setChangeTicket('')
    } catch (err) {
      console.error(err)
      setError('Run could not be started. Check credentials and try again.')
    } finally {
      setLoading(false)
      setTimeout(() => setSuccess(null), 5000)
    }
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-6">
        <p className="text-sm text-gray-600">Operations</p>
        <h1 className="text-3xl font-bold text-gray-900">Orchestration Console</h1>
        <p className="text-gray-700 mt-2 max-w-3xl">
          Launch curated infrastructure workflows that coordinate Terraform environments,
          Ansible playbooks, and OTEL-enabled services. Each run is tracked with
          runbook links, parameters, and audit-friendly outputs.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {plans.map((plan) => (
          <button
            key={plan.id}
            onClick={() => setSelectedPlanId(plan.id)}
            className={`text-left border rounded-lg p-4 shadow-sm transition ${
              selectedPlanId === plan.id ? 'border-primary-500 ring-2 ring-primary-100' : 'border-gray-200'
            }`}
          >
            <p className="text-xs uppercase tracking-wide text-gray-500">{plan.environment}</p>
            <p className="text-lg font-semibold text-gray-900">{plan.name}</p>
            <p className="text-sm text-gray-700 mt-2">{plan.description}</p>
            <div className="mt-3 text-xs text-gray-600 space-y-1">
              <p>Playbook: {plan.playbook_path}</p>
              <p>Terraform: {plan.tfvars_file}</p>
              <p>Runbook: {plan.runbook}</p>
            </div>
          </button>
        ))}
      </div>

      <div className="mt-6 bg-white shadow rounded-lg p-4 border">
        <h2 className="text-xl font-semibold text-gray-900">Launch run</h2>
        <p className="text-sm text-gray-600 mt-1">
          Provide change metadata to capture why the rollout is occurring. A healthy status should
          appear within seconds when using the baked-in dry-run checks.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Plan</label>
            <select
              value={selectedPlanId}
              onChange={(e) => setSelectedPlanId(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Change ticket</label>
            <input
              type="text"
              value={changeTicket}
              onChange={(e) => setChangeTicket(e.target.value)}
              placeholder="CHG-12345"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Change window</label>
            <select
              value={windowLabel}
              onChange={(e) => setWindowLabel(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="standard">Standard</option>
              <option value="expedited">Expedited</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
        </div>
        <div className="mt-4 flex items-center space-x-3">
          <button
            onClick={triggerRun}
            disabled={loading || !selectedPlanId}
            className="btn-primary"
          >
            {loading ? 'Starting...' : 'Start orchestration'}
          </button>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          {success && <p className="text-sm text-emerald-700">{success}</p>}
        </div>
      </div>

      <div className="mt-6 bg-white shadow rounded-lg p-4 border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Run history</h2>
            <p className="text-sm text-gray-600">Most recent orchestration events</p>
          </div>
          {latestRun && (
            <div className={`px-3 py-1 rounded-full text-sm border ${statusStyles[latestRun.status]}`}>
              Latest: {latestRun.status}
            </div>
          )}
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Run</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Plan</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Status</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Change ticket</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Started</th>
                <th className="px-4 py-2 text-left text-xs font-semibold text-gray-700">Artifacts</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {runs.map((run) => (
                <tr key={run.id}>
                  <td className="px-4 py-2 text-sm text-gray-900">{run.id.slice(0, 8)}</td>
                  <td className="px-4 py-2 text-sm text-gray-700">{run.plan_id}</td>
                  <td className="px-4 py-2 text-sm">
                    <span className={`px-2 py-1 rounded-full border ${statusStyles[run.status]}`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-700">
                    {run.parameters.change_ticket || 'N/A'}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-700">
                    {new Date(run.started_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-600">
                    <div className="space-y-1">
                      <p>Playbook: {run.artifacts.playbook}</p>
                      <p>Terraform: {run.artifacts.tfvars}</p>
                      {run.artifacts.runbook && (
                        <p className="text-primary-600">Runbook: {run.artifacts.runbook}</p>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {runs.length === 0 && (
            <div className="p-6 text-center text-gray-600">No runs recorded yet</div>
          )}
        </div>
      </div>
    </div>
  )
}
