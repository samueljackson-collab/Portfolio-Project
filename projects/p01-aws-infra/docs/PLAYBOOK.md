# P01 · AWS Infrastructure Automation — Incident Response Playbook

> **Purpose:** Provide actionable, scenario-based guidance to detect, respond to, resolve, and learn from incidents impacting the AWS landing zone and hosted services.

---
## 1. Incident Classification
| Severity | Description | Target Response | Target Resolution |
| --- | --- | --- | --- |
| **P1 — Critical** | Complete outage or security breach with customer impact. | 5 minutes | 1 hour |
| **P2 — High** | Degraded service with partial customer impact or security exposure. | 15 minutes | 4 hours |
| **P3 — Medium** | Non-critical functionality impaired, workaround available. | 1 hour | 24 hours |
| **P4 — Low** | Cosmetic issues, documentation fixes, process gaps. | 1 business day | 5 business days |

Escalation path: Primary On-Call → Secondary → Director of Engineering → CTO. Update Slack `#status-landing-zone` and PagerDuty incident notes.

---
## 2. Response Workflow
1. **Detect** — Alert triggers via CloudWatch/Prometheus. PagerDuty routes to on-call.  
2. **Triage** — Classify severity, gather metrics/logs, determine blast radius.  
3. **Stabilize** — Execute containment steps (disable deploys, scale resources, failover).  
4. **Resolve** — Implement fix (rollback, configuration update, resource scaling).  
5. **Communicate** — Provide status updates at defined cadence (see templates).  
6. **Recover** — Validate services, re-enable automation, capture timelines.  
7. **Learn** — Schedule post-incident review, update documentation and runbooks.  

---
## 3. Communication Templates
### 3.1 Initial External Update (P1/P2)
```
Status: Investigating P1 incident impacting production. Customers may experience errors accessing the service. On-call engineering is engaged; next update in 30 minutes.
```

### 3.2 Internal Slack Update
```
:P1: Incident INC-####
- Start: 2025-10-06 03:12 UTC
- Impact: 5xx errors on /api/* endpoints (approx 40% traffic)
- Actions: Rolled back ASG launch template, investigating database connectivity
- Next Update: 03:42 UTC
```

### 3.3 Post-Mortem Summary
- **Incident ID:** INC-####  
- **Timeline:** Detection → Triage → Resolution milestones.  
- **Root Cause:** What/why.  
- **Impact:** Duration, customers, metrics.  
- **Lessons & Actions:** Preventive measures, documentation updates.  
- **Owners:** Primary & secondary engineers.  

---
## 4. Incident Scenarios
### P1-INC-001 · Complete Service Outage
- **Trigger:** ALB 5xx > 40%, traffic routed to error page.  
- **Runbook:**
  1. Confirm ALB target health, Auto Scaling activity.  
  2. Execute launch template rollback to last known good version.  
  3. Validate database connectivity; if failing, failover to read replica.  
  4. Post-resolution, run `security-audit.sh` to validate configuration drift.  

### P1-INC-002 · Database Connectivity Loss
- **Trigger:** RDS connection errors, CloudWatch alarm `LandingZone-RDSConnectionErrors`.  
- **Response:**
  1. Check RDS status (maintenance, failover).  
  2. Validate subnet route tables and security groups.  
  3. Promote read replica if primary failure persists > 15 minutes.  
  4. Notify stakeholders about potential data consistency checks.  

### P1-INC-003 · Security Breach (IAM Compromise)
- **Trigger:** GuardDuty `CredentialAccess:IAMUser/AnomalousBehavior`.  
- **Response:**
  1. Disable suspected credentials, rotate keys.  
  2. Review CloudTrail for unauthorized actions, isolate resources.  
  3. Enable SCP lockdown for non-essential accounts.  
  4. Engage security team; follow breach notification policy.  
  5. Run forensic scripts, preserve logs.  

### P1-INC-004 · Region Outage
- **Trigger:** AWS Health event for primary region.  
- **Response:**
  1. Invoke `dr-drill.sh --mode failover` to spin workloads in secondary region.  
  2. Update DNS via Route53 weighted routing.  
  3. Monitor replication lag, ensure data consistency.  
  4. Communicate fallback timeline (target 30 minutes).  

### P2-INC-005 · Elevated Latency
- **Trigger:** p95 latency > 400 ms for 15 minutes.  
- **Response:** Scale ASG desired capacity, inspect ALB logs, confirm downstream services.  
- **Root Cause Hunting:** Check new deploys, DB slow queries, increased traffic.  

### P2-INC-006 · Certificate Expiration Imminent
- **Trigger:** ACM certificate < 15 days to expiry.  
- **Response:** Request/validate new certificate, update CloudFront/ALB, confirm distribution status.  

### P2-INC-007 · NAT Gateway Cost Spike
- **Trigger:** Cost anomaly detection > 120% egress cost.  
- **Response:** Inspect VPC Flow Logs, identify large data transfers, confirm legitimate usage, consider VPC endpoints.  

### P3-INC-008 · Disk Utilization Growth
- **Trigger:** EBS volume usage > 75%.  
- **Response:** Extend volume, schedule maintenance, update capacity plan.  

### P3-INC-009 · Backup Job Warning
- **Trigger:** Backup copy job missed schedule.  
- **Response:** Re-run backup, validate retention, investigate AWS Backup logs.  

### P3-INC-010 · Terraform Drift Detected
- **Trigger:** `terraform plan` shows unexpected resources.  
- **Response:** Identify manual changes, revert to IaC, document follow-up tasks.  

### P4-INC-011 · Documentation Gap
- **Trigger:** Feedback indicating missing steps.  
- **Response:** Create PR updating relevant docs, capture knowledge in Confluence/Notion.  

### Additional Scenarios
- **P2-INC-012:** CloudFront 5xx spike due to origin issues.  
- **P2-INC-013:** WAF blocking legitimate traffic (adjust rules, test).  
- **P3-INC-014:** IAM Access Analyzer warning for new policy.  
- **P3-INC-015:** Scheduled maintenance window aborted.  
- **P4-INC-016:** Automated report failed (rerun script, fix cron).  

---
## 5. Automation Hooks
- PagerDuty webhooks trigger automation pipeline to collect metrics snapshots (`scripts/security-audit.sh`).  
- Slack slash command `/status p01` posts current runbook status and latest checks.  
- GitHub Actions job `incident-artifacts` packages Terraform plans, CloudTrail logs for post-incident review.  

---
## 6. Post-Incident Review Template
1. **Summary:** High-level description and impact.  
2. **Timeline:** Detection, containment, resolution, communications.  
3. **Root Cause Analysis:** 5 Whys or Fishbone diagram.  
4. **Impact Assessment:** Customers, revenue, SLA breaches.  
5. **Action Items:** Preventive, detective, responsive measures with owners/due dates.  
6. **Follow-Up:** Runbook/playbook updates, training sessions, automation improvements.  

---
## 7. References
- Runbook operations schedule: [docs/RUNBOOK.md](./RUNBOOK.md)  
- Terraform modules: [`infra/modules`](../infra/modules)  
- PagerDuty service: `AWS-Landing-Zone`  
- Slack channels: `#status-landing-zone`, `#ops-alerts`  
- Knowledge base: Confluence space `OPS-P01`  

