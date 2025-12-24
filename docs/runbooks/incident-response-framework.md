# Incident Response Framework

## Overview

This document defines the incident response process, roles, responsibilities, and communication procedures for production incidents.

## Incident Response Lifecycle

```
1. DETECT → 2. TRIAGE → 3. MITIGATE → 4. RESOLVE → 5. POSTMORTEM
```

### 1. Detection (0-5 minutes)

**How incidents are detected:**
- Automated monitoring alerts (Prometheus, Grafana)
- PagerDuty notifications
- User reports via support channels
- Manual observation

**Immediate Actions:**
- Acknowledge the alert
- Create incident in tracking system
- Post in #incident-response Slack channel

### 2. Triage (5-15 minutes)

**Objectives:**
- Assess severity and impact
- Determine if escalation is needed
- Assign incident commander
- Establish war room

**Quick Health Check Commands:**
```bash
# Check pod status
kubectl get pods -n production

# Check resource utilization
kubectl top pods -n production

# Check recent deployments
kubectl rollout history deployment/app -n production

# View recent logs
kubectl logs -n production deployment/app --tail=100 --since=10m

# Check metrics
curl https://prometheus/api/v1/query?query=up
```

**Severity Assessment:**

| Criteria | P0 | P1 | P2 | P3 |
|----------|----|----|----|----|
| Users Affected | >50% | 10-50% | 1-10% | <1% |
| Service Status | Down | Degraded | Slow | Minor issue |
| Data Loss Risk | High | Medium | Low | None |
| Revenue Impact | Critical | High | Medium | Low |
| Response Time | 15 min | 1 hour | 4 hours | 24 hours |

### 3. Mitigation (15-60 minutes)

**Goal:** Reduce immediate impact while root cause is being investigated

**Common Mitigation Strategies:**

#### Rollback Recent Deployment
```bash
# Rollback to previous version
kubectl rollout undo deployment/app -n production

# Check rollback status
kubectl rollout status deployment/app -n production

# Verify health
kubectl get pods -n production -l app=myapp
```

#### Scale Resources
```bash
# Scale up to handle increased load
kubectl scale deployment/app -n production --replicas=15

# Enable horizontal pod autoscaler
kubectl autoscale deployment/app -n production \
  --cpu-percent=70 \
  --min=5 \
  --max=25
```

#### Route Traffic
```bash
# Drain specific node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Remove failing pods
kubectl delete pod <pod-name> -n production

# Update service to exclude unhealthy pods
kubectl set selector service/app "app=myapp,healthy=true"
```

#### Enable Circuit Breakers
```bash
# Update deployment with circuit breaker configuration
kubectl set env deployment/app -n production \
  CIRCUIT_BREAKER_ENABLED=true \
  CIRCUIT_BREAKER_THRESHOLD=50 \
  CIRCUIT_BREAKER_TIMEOUT=30000
```

### 4. Resolution (Variable)

**Objectives:**
- Identify and fix root cause
- Deploy permanent solution
- Verify incident is resolved
- Monitor for recurrence

**Resolution Workflow:**
1. Identify root cause through investigation
2. Develop and test fix
3. Deploy fix using gradual rollout
4. Monitor key metrics for 30 minutes
5. Confirm incident resolved
6. Close incident

**Gradual Rollout Example:**
```bash
# Canary deployment - 10% traffic
kubectl set image deployment/app -n production \
  app=myapp:v2.1.0 \
  --record

kubectl patch deployment app -n production -p \
  '{"spec":{"strategy":{"rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'

# Monitor canary
watch kubectl get pods -n production -l app=myapp,version=v2.1.0

# If successful, continue rollout
kubectl rollout resume deployment/app -n production
```

### 5. Postmortem (Within 48 hours)

**Required for:** P0 and P1 incidents
**Optional for:** P2 and P3 incidents

**Postmortem Template:** See [README.md](./README.md#postmortem-template)

**Key Components:**
- Blameless timeline of events
- Root cause analysis (5 Whys)
- Action items with owners and due dates
- Metrics and impact quantification

## Roles & Responsibilities

### Incident Commander (IC)
**Responsibilities:**
- Lead incident response
- Make critical decisions
- Coordinate team activities
- Manage communications
- Ensure postmortem is completed

**Selection:** First senior engineer to acknowledge P0/P1 incident

### Technical Lead
**Responsibilities:**
- Deep technical investigation
- Develop and implement fix
- Advise incident commander
- Update technical documentation

### Communications Lead
**Responsibilities:**
- Update status page
- Send customer notifications
- Post internal updates
- Coordinate with support team

### Subject Matter Experts (SMEs)
**Responsibilities:**
- Provide domain expertise
- Execute specific remediation tasks
- Support investigation

## Communication Procedures

### Internal Communication

#### Initial Alert (Post immediately)
```
🚨 INCIDENT DETECTED - P[0-3]

Service: [service-name]
Symptom: [description of what's broken]
Impact: [% of users affected, features down]
Start Time: [timestamp]
Status: 🔍 Investigating

War Room: [Zoom/Slack link]
Incident Commander: @[name]
Status Updates: Every 15 minutes

#incident-[YYYYMMDD-HHMM]
```

#### Status Update (Every 15-30 minutes)
```
📊 INCIDENT UPDATE #[number] - [HH:MM]

Current Status: [🔍 Investigating | 🔧 Mitigating | ✅ Resolved | 👀 Monitoring]

Impact:
- [Current user impact]
- [Affected services/features]

Actions Taken:
- ✅ [Completed action 1]
- ✅ [Completed action 2]
- 🔄 [In-progress action]

Root Cause: [Brief description or "Still investigating"]

Next Steps:
- [ ] [Planned action 1]
- [ ] [Planned action 2]

ETA to Resolution: [estimated time or "Unknown"]

Incident Commander: @[name]
#incident-[YYYYMMDD-HHMM]
```

#### Resolution Notification
```
✅ INCIDENT RESOLVED

Incident: [title]
Duration: [total time from detection to resolution]
Impact: [summary of impact]

Root Cause: [brief technical explanation]

Resolution: [what fixed it]

Next Steps:
- Continued monitoring for [timeframe]
- Postmortem scheduled for [date/time]
- Follow-up actions: [link to action items]

Thank you to the response team: @[names]

Postmortem: [link when available]
#incident-[YYYYMMDD-HHMM]
```

### External Communication

#### Status Page Update - Initial
```
Investigating - [Service Name]

We are investigating reports of [description of issue].
Users may experience [specific impact].

We will provide updates as more information becomes available.

Posted at: [timestamp]
```

#### Status Page Update - Identified
```
Identified - [Service Name]

We have identified the cause of [issue] as [brief explanation].
Our team is working on a fix.

Affected services: [list]
Estimated resolution: [timeframe or "Unknown"]

Posted at: [timestamp]
```

#### Status Page Update - Resolved
```
Resolved - [Service Name]

The issue with [service] has been resolved.
All services are operating normally.

Root cause: [brief, non-technical explanation]
Duration: [time]

We apologize for any inconvenience.

Posted at: [timestamp]
```

#### Customer Notification Email (for P0 incidents)
```
Subject: Service Disruption - [Date]

Dear Valued Customer,

We experienced a service disruption affecting [service/feature]
on [date] from [start time] to [end time] ([duration]).

What happened:
[Non-technical explanation of the incident]

Impact:
[Specific impact to customers]

Resolution:
[What we did to fix it]

Prevention:
We have implemented the following measures to prevent recurrence:
- [Preventive measure 1]
- [Preventive measure 2]

We sincerely apologize for any inconvenience this may have caused.
If you have any questions or concerns, please contact our support team.

Thank you for your patience and understanding.

Best regards,
[Team Name]
```

## Escalation Procedures

### P0 Incidents
1. PagerDuty alerts on-call engineer (immediate)
2. On-call acknowledges within 5 minutes
3. Incident commander establishes war room
4. Notify engineering leadership within 15 minutes
5. Notify executive leadership if impact >1 hour

### P1 Incidents
1. Alert via Slack #incident-response
2. On-call engineer acknowledges within 30 minutes
3. Assign incident commander
4. Notify engineering lead within 1 hour

### P2/P3 Incidents
1. Create ticket in issue tracker
2. Assign to appropriate team
3. No immediate escalation required

## Tools & Systems

### Monitoring & Alerting
- **Prometheus/Grafana**: Metrics and dashboards
- **PagerDuty**: Alert routing and escalation
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing

### Communication
- **Slack**: #incident-response channel
- **Zoom**: War room meetings
- **Statuspage.io**: External status updates
- **Email**: Customer notifications

### Incident Management
- **Jira**: Incident tracking
- **Confluence**: Postmortems
- **GitHub**: Code changes and deployments

### Access & Permissions
```bash
# Emergency access (break-glass)
# Requires approval from two leads

# Assume emergency role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT:role/EmergencyAccess \
  --role-session-name incident-response-session

# Access production database (read-only)
kubectl exec -it -n production db-proxy -- psql -U readonly

# View production secrets (audit logged)
# View a specific secret key (e.g., 'API_KEY'), decoded
kubectl get secret -n production app-secrets -o jsonpath='{.data.API_KEY}' | base64 --decode
```

## Incident Metrics

### Key Performance Indicators

**MTTD (Mean Time to Detect)**
- Target: <5 minutes
- Measurement: Alert timestamp - Actual incident start

**MTTA (Mean Time to Acknowledge)**
- Target: <5 minutes for P0, <30 minutes for P1
- Measurement: Engineer acknowledgment - Alert timestamp

**MTTM (Mean Time to Mitigate)**
- Target: <15 minutes for P0, <1 hour for P1
- Measurement: Impact reduced - Alert acknowledged

**MTTR (Mean Time to Resolve)**
- Target: <1 hour for P0, <4 hours for P1
- Measurement: Incident resolved - Incident start

### Monthly Reporting

```markdown
## Incident Report - [Month Year]

### Summary
- Total Incidents: [count]
  - P0: [count]
  - P1: [count]
  - P2: [count]
  - P3: [count]

### Metrics
- MTTD: [average]
- MTTA: [average]
- MTTM: [average]
- MTTR: [average]

### Top Incident Categories
1. [Category]: [count] incidents
2. [Category]: [count] incidents
3. [Category]: [count] incidents

### Action Items Completed
- [Completed action 1]
- [Completed action 2]

### Ongoing Improvements
- [In-progress improvement 1]
- [In-progress improvement 2]
```

## On-Call Procedures

### On-Call Rotation
- **Duration**: 1 week (Monday 9am - Monday 9am)
- **Coverage**: 24/7
- **Handoff**: Monday morning sync
- **Tool**: PagerDuty schedule

### On-Call Responsibilities
- Respond to P0/P1 incidents within 5 minutes
- Acknowledge all alerts within 15 minutes
- Escalate if unable to resolve within 30 minutes
- Document all incidents in tracking system
- Update runbooks after incidents

### On-Call Preparation
```bash
# Verify access before rotation starts
kubectl get pods -n production
aws sts get-caller-identity
psql -h production-db -U readonly -c "SELECT 1"

# Test alerting
# ⚠️  SECURITY: Never paste real tokens into documentation or scripts
# Use environment variables instead:
curl -X POST https://events.pagerduty.com/v2/enqueue \
  -H "Authorization: Token token=${PAGERDUTY_TOKEN}" \
    -d '{"routing_key":"YOUR_KEY","event_action":"trigger"}'
  -d '{"routing_key":"YOUR_KEY","event_action":"trigger"}'

# Review recent incidents
# Check known issues board
# Read latest postmortems
```

### Handoff Template
```markdown
## On-Call Handoff - [Date]

### Incidents This Week
- [Incident 1]: [Brief summary and status]
- [Incident 2]: [Brief summary and status]

### Ongoing Issues
- [Issue 1]: [Description and owner]
- [Issue 2]: [Description and owner]

### Upcoming
- Scheduled maintenance: [Date/time]
- Expected high traffic: [Date/time]

### Notes
- [Any special considerations]
```

## Best Practices

### Do's
✅ Follow the runbook procedures
✅ Document everything in real-time
✅ Communicate frequently and clearly
✅ Focus on mitigation before root cause
✅ Stay calm and methodical
✅ Ask for help when needed
✅ Preserve evidence before making changes

### Don'ts
❌ Make changes without documenting
❌ Blame individuals
❌ Skip communication steps
❌ Work in isolation
❌ Delay escalation
❌ Delete logs or evidence
❌ Deploy untested fixes to production

## Training & Drills

### Monthly Chaos Engineering
- Scheduled chaos tests (first Tuesday)
- Unannounced scenarios (random)
- Post-drill retrospective

### Quarterly DR Drill
- Full disaster recovery simulation
- All teams participate
- Timed execution
- Runbook validation

### Annual Security Drill
- Simulated breach scenario
- Test security runbooks
- Legal/compliance involvement

---

**Last Updated**: December 2024
**Document Owner**: DevOps Team
**Review Frequency**: Quarterly
