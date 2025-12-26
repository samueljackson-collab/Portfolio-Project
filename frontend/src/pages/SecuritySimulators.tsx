import React, { useEffect, useState } from 'react'
import {
  DeploymentSummary,
  DetectionRule,
  Endpoint,
  Hypothesis,
  Incident,
  MalwareDetail,
  MalwareSample,
  Operation,
  OperationEvent,
  SocAlert,
  edrService,
  huntingService,
  malwareService,
  ransomwareService,
  redTeamService,
  socService
} from '../api'
import {
  DeploymentSummaryCard,
  EdrEndpointTable,
  HuntingBoard,
  MalwareReportCard,
  RansomwareTimeline,
  RedTeamTimeline,
  SocAlertTable
} from '../components/security/SimulationBlocks'

const Section: React.FC<{ title: string; children: React.ReactNode; subtitle?: string }> = ({
  title,
  children,
  subtitle
}) => (
  <div className="bg-white shadow rounded-lg p-6 space-y-3">
    <div>
      <h2 className="text-xl font-bold text-gray-900">{title}</h2>
      {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
    </div>
    {children}
  </div>
)

const SecuritySimulators: React.FC = () => {
  const [operations, setOperations] = useState<Operation[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [alerts, setAlerts] = useState<SocAlert[]>([])
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([])
  const [rules, setRules] = useState<DetectionRule[]>([])
  const [malware, setMalware] = useState<MalwareDetail | null>(null)
  const [samples, setSamples] = useState<MalwareSample[]>([])
  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [deployment, setDeployment] = useState<DeploymentSummary | null>(null)

  useEffect(() => {
    const load = async () => {
      const [ops, incs, existingAlerts, hyps, rulesData, eps, summary] = await Promise.all([
        redTeamService.listOperations(),
        ransomwareService.listIncidents(),
        socService.listAlerts(),
        huntingService.listHypotheses(),
        huntingService.listRules(),
        edrService.listEndpoints(),
        edrService.deploymentSummary()
      ])
      setOperations(ops)
      setIncidents(incs)
      setAlerts(existingAlerts)
      setHypotheses(hyps)
      setRules(rulesData)
      setEndpoints(eps)
      setDeployment(summary)
    }
    load().catch(console.error)
  }, [])

  const createOperation = async () => {
    const op = await redTeamService.createOperation({ name: '90-day APT', objective: 'Demonstrate stealth' })
    setOperations((prev) => [...prev, { ...op, events: [] as OperationEvent[] }])
  }

  const simulateOperation = async (operationId: string) => {
    await redTeamService.simulate(operationId, 3)
    const updated = await redTeamService.listOperations()
    setOperations(updated)
  }

  const createIncident = async () => {
    const incident = await ransomwareService.createIncident({ name: 'Ransomware Drill' })
    const updated = await ransomwareService.simulate(incident.id)
    setIncidents((prev) => [...prev, updated])
  }

  const generateAlerts = async () => {
    const generated = await socService.generateAlerts()
    setAlerts(generated)
  }

  const createHypothesis = async () => {
    const hypothesis = await huntingService.createHypothesis({
      title: 'PowerShell lateral movement',
      description: 'Track WinRM and PSRemoting artifacts'
    })
    const finding = await huntingService.addFinding(hypothesis.id, {
      severity: 'high',
      details: 'Encoded command in event log'
    })
    const rule = await huntingService.promoteFinding(finding.id)
    setHypotheses((prev) => [...prev, hypothesis])
    setRules((prev) => [...prev, rule])
  }

  const createSample = async () => {
    const sample = await malwareService.createSample({ name: 'locker-sim', file_hash: 'ff11aa22', sample_type: 'pe' })
    setSamples((prev) => [...prev, sample])
    const detail = await malwareService.analyze(sample.id)
    setMalware(detail)
  }

  const registerEndpoint = async () => {
    await edrService.registerEndpoint({ hostname: `agent-${endpoints.length + 1}`, operating_system: 'linux', agent_version: '1.0.0' })
    const eps = await edrService.listEndpoints()
    setEndpoints(eps)
    setDeployment(await edrService.deploymentSummary())
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Security Simulators</h1>
        <p className="text-gray-600">Red/Blue team labs with day-by-day visibility and automation hooks.</p>
      </div>

      <Section title="Red Team Operation Simulator" subtitle="90-day APT with stealth vs detection visuals">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={createOperation}>
            Create Operation
          </button>
          {operations[0] && (
            <button className="btn-secondary" onClick={() => simulateOperation(operations[0].id)}>
              Simulate Next Day
            </button>
          )}
        </div>
        {operations.map((op) => (
          <div key={op.id} className="border rounded p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-semibold">{op.name}</p>
                <p className="text-sm text-gray-600">Undetected streak: {op.undetected_streak}</p>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-blue-50 text-blue-700">{op.status}</span>
            </div>
            <RedTeamTimeline events={op.events || []} />
          </div>
        ))}
      </Section>

      <Section title="Ransomware Response" subtitle="Lifecycle simulation with ordered milestones">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={createIncident}>
            Create & Simulate Incident
          </button>
        </div>
        {incidents.map((incident) => (
          <div key={incident.id} className="border rounded p-4">
            <div className="flex items-center justify-between">
              <p className="font-semibold">{incident.name}</p>
              <span className="text-xs text-gray-600">{incident.status}</span>
            </div>
            <RansomwareTimeline events={incident.events || []} />
            {incident.warning && <p className="text-xs text-amber-600">{incident.warning}</p>}
          </div>
        ))}
      </Section>

      <Section title="SOC Portal" subtitle="Alerts, cases, and playbooks in one view">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={generateAlerts}>
            Generate Alerts
          </button>
          <button className="btn-secondary" onClick={async () => setAlerts(await socService.listAlerts())}>
            Refresh
          </button>
        </div>
        <SocAlertTable alerts={alerts} />
      </Section>

      <Section title="Threat Hunting" subtitle="Promote findings into draft detection rules">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={createHypothesis}>
            Add Hypothesis
          </button>
        </div>
        <HuntingBoard hypotheses={hypotheses} rules={rules} />
      </Section>

      <Section title="Malware Analysis Lab" subtitle="Simulated static/dynamic analysis with YARA output">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={createSample}>
            Upload Sample
          </button>
        </div>
        {malware && (
          <div className="mt-3">
            <p className="text-sm text-gray-600 mb-1">Sample: {malware.sample.name}</p>
            <MalwareReportCard report={malware.report} />
          </div>
        )}
        {samples.length > 0 && (
          <p className="text-xs text-gray-500">{samples.length} sample(s) tracked in this session.</p>
        )}
      </Section>

      <Section title="EDR Platform" subtitle="Endpoint coverage and policy toggles">
        <div className="flex items-center space-x-3">
          <button className="btn-primary" onClick={registerEndpoint}>
            Register Endpoint
          </button>
          <button className="btn-secondary" onClick={async () => setDeployment(await edrService.deploymentSummary())}>
            Refresh Coverage
          </button>
        </div>
        <DeploymentSummaryCard summary={deployment} />
        <EdrEndpointTable endpoints={endpoints} />
      </Section>
    </div>
  )
}

export default SecuritySimulators

