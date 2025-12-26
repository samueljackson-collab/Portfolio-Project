import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  DeploymentSummaryCard,
  EdrEndpointTable,
  HuntingBoard,
  MalwareReportCard,
  RansomwareTimeline,
  RedTeamTimeline,
  SocAlertTable
} from '../components/security/SimulationBlocks'

describe('Security simulation components', () => {
  it('renders detected vs covert events in the red team timeline', () => {
    render(
      <RedTeamTimeline
        events={[
          {
            id: '1',
            operation_id: 'op',
            day: 1,
            timestamp: '',
            description: 'Test',
            category: 'Recon',
            detected: true,
            detection_confidence: 0.9
          },
          {
            id: '2',
            operation_id: 'op',
            day: 2,
            timestamp: '',
            description: 'Stealth',
            category: 'C2',
            detected: false,
            detection_confidence: 0.2
          }
        ]}
      />
    )

    expect(screen.getByText('Detected')).toBeInTheDocument()
    expect(screen.getByText('Covert')).toBeInTheDocument()
  })

  it('renders ordered ransomware lifecycle steps', () => {
    render(
      <RansomwareTimeline
        events={[
          { id: '1', incident_id: 'i1', sequence: 0, type: 'Detection', details: 'Alert', timestamp: '' },
          { id: '2', incident_id: 'i1', sequence: 1, type: 'Containment', details: 'Isolate', timestamp: '' }
        ]}
      />
    )

    const items = screen.getAllByRole('listitem')
    expect(items[0].textContent).toContain('Detection')
    expect(items[1].textContent).toContain('Containment')
  })

  it('renders severity styling for SOC alerts', () => {
    render(
      <SocAlertTable
        alerts={[
          {
            id: 'a1',
            title: 'Brute force',
            description: 'SSH failures',
            severity: 'high',
            status: 'open',
            source: 'sensor',
            created_at: '',
            updated_at: ''
          }
        ]}
      />
    )

    expect(screen.getByText('Brute force')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })

  it('shows promoted rules on the hunting board', () => {
    render(
      <HuntingBoard
        hypotheses={[
          { id: 'h1', title: 'PowerShell', description: '', status: 'open', created_at: '', updated_at: '' }
        ]}
        rules={[{ id: 'r1', name: 'Rule', query: 'search', status: 'Draft', source_finding_id: '', created_at: '' }]}
      />
    )

    expect(screen.getByText('Rule')).toBeInTheDocument()
    expect(screen.getByText('PowerShell')).toBeInTheDocument()
  })

  it('renders malware YARA output', () => {
    render(
      <MalwareReportCard
        report={{
          id: 'r1',
          sample_id: 's1',
          static_analysis: 'packer detected',
          dynamic_analysis: 'callback observed',
          iocs: [],
          yara_rule: 'rule test {}',
          created_at: ''
        }}
      />
    )

    expect(screen.getByText('YARA Rule')).toBeInTheDocument()
    expect(screen.getByText('packer detected')).toBeInTheDocument()
  })

  it('flags offline or outdated endpoints', () => {
    render(
      <>
        <EdrEndpointTable
          endpoints={[
            {
              id: 'e1',
              hostname: 'host1',
              operating_system: 'linux',
              agent_version: '1.0.0',
              last_checkin: '',
              online: false,
              created_at: '',
              updated_at: ''
            }
          ]}
        />
        <DeploymentSummaryCard
          summary={{ total_endpoints: 1, online: 0, outdated_agents: 1, coverage: 0, active_policies: 2 }}
        />
      </>
    )

    expect(screen.getByText('host1')).toBeInTheDocument()
    expect(screen.getByText('Outdated')).toBeInTheDocument()
    expect(screen.getByText('Total')).toBeInTheDocument()
  })
})
