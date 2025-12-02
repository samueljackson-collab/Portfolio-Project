import React, { useEffect, useState } from 'react'

interface DeploymentPlan {
  terraform_plan: string
  ansible_playbook: string
  checks: string[]
}

interface EnvironmentState {
  environment: string
  status: string
  artifact_version: string
  last_deploy: string
  plan: DeploymentPlan
  notes: string[]
}

const statusColor: Record<string, string> = {
  healthy: 'bg-green-100 text-green-700',
  draining: 'bg-yellow-100 text-yellow-700',
  'in-progress': 'bg-blue-100 text-blue-700',
  planned: 'bg-slate-100 text-slate-700',
}

export const OrchestrationConsole: React.FC = () => {
  const [environments, setEnvironments] = useState<EnvironmentState[]>([])
  const [error, setError] = useState<string>('')

  useEffect(() => {
    fetch('/orchestration/environments')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to load environment state')
        }
        return res.json()
      })
      .then(setEnvironments)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Platform Orchestration</h1>
          <p className="text-gray-600">
            Terraform + Ansible blueprints, deploy receipts, and health summaries.
          </p>
        </div>
        <div className="bg-indigo-50 border border-indigo-100 px-4 py-2 rounded-lg text-indigo-700 text-sm">
          Endpoints: /orchestration/environments &amp; /orchestration/deploy
        </div>
      </div>

      {error && <div className="mt-4 text-red-600">{error}</div>}

      <div className="grid md:grid-cols-2 gap-4 mt-6">
        {environments.map((env) => (
          <div key={env.environment} className="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{env.environment.toUpperCase()}</p>
                <p className="text-xl font-semibold text-gray-900">{env.artifact_version}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor[env.status] || 'bg-gray-100 text-gray-700'}`}>
                {env.status}
              </span>
            </div>
            <dl className="mt-4 space-y-2 text-sm text-gray-700">
              <div className="flex justify-between"><dt>Last Deploy</dt><dd>{new Date(env.last_deploy).toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt>Terraform</dt><dd className="text-indigo-600 font-mono">{env.plan.terraform_plan}</dd></div>
              <div className="flex justify-between"><dt>Ansible</dt><dd className="text-indigo-600 font-mono">{env.plan.ansible_playbook}</dd></div>
            </dl>
            <div className="mt-3">
              <p className="text-xs font-semibold text-gray-500">Pre-flight checks</p>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                {env.plan.checks.map((check) => (
                  <li key={check}>{check}</li>
                ))}
              </ul>
            </div>
            <div className="mt-3">
              <p className="text-xs font-semibold text-gray-500">Notes</p>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                {env.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
