# P01 · AWS Infrastructure Automation — Operations Runbook

> **Audience:** On-call engineers and operations analysts responsible for day-to-day management of the AWS landing zone and hosted workloads.

---
## 1. Contact & Escalation
- **Primary On-Call:** Systems Development Engineer (PagerDuty schedule `SDE-Primary`).  
- **Secondary:** Cloud Platform Lead (`+1-555-0100`).  
- **Escalation Path:** Primary → Secondary → Director of Engineering → CTO.  
- **Vendors:** AWS Enterprise Support (Account ID documented in vault), Domain registrar (Namecheap), CDN (CloudFront).  

---
## 2. Environment Summary
| Environment | Purpose | Change Window | Notes |
| --- | --- | --- | --- |
| Production | Customer-facing workloads | Wed 22:00–23:30 UTC | Strict change approval required; backup retention 35 days. |
| Staging | Pre-production validation | Daily 03:00–05:00 UTC | Mirrors production networking with reduced scaling. |
| Sandbox | Experimentation | Anytime | Auto-destroy resources nightly via scheduler. |

---
## 3. Daily Procedures
| Time (UTC) | Task | Responsible | Tooling |
| --- | --- | --- | --- |
| 00:00 | Review overnight alerts & incidents | Primary | PagerDuty, Slack #ops-alerts |
| 04:00 | Validate CloudWatch dashboards for anomalies | Primary | CloudWatch, Grafana |
| 08:00 | Check cost anomaly report | Primary | AWS Budgets email, Cost Explorer |
| 12:00 | Confirm backups succeeded (RDS, EBS snapshots) | Secondary | AWS Console, `scripts/daily-health-check.sh` |
| 16:00 | Inspect Terraform state lock table for stale entries | Primary | DynamoDB console, AWS CLI |
| 20:00 | Rotate break-glass credentials (verify sealed) | Secondary | Secrets Manager |

**Automation:** Execute `scripts/daily-health-check.sh` once per shift; attach output to daily ops ticket.

---
## 4. Weekly Procedures
- **Monday:** Patch status review via SSM compliance report; open tickets for drift.  
- **Wednesday:** Cost optimization meeting, update FinOps dashboard.  
- **Thursday:** Security review (IAM Access Analyzer findings, GuardDuty alerts).  
- **Friday:** Run `scripts/weekly-report.sh`, distribute to leadership and archive in knowledge base.  

Checklist:
- [ ] RDS performance insights reviewed, anomalies triaged.  
- [ ] Auto Scaling activity logs exported.  
- [ ] Terraform module versions bumped where patches exist.  

---
## 5. Monthly Procedures
1. Conduct disaster recovery drill using `scripts/dr-drill.sh` and document outcomes.  
2. Validate IAM access reviews; disable stale accounts.  
3. Rotate KMS CMK aliases per policy and confirm key policies.  
4. Update architecture diagrams and metrics thresholds if workload changed.  
5. Execute tabletop incident simulation with cross-functional team.  

---
## 6. Change Management
- **Request Format:** Jira ticket with summary, impact analysis, rollback, test evidence.  
- **Approval Requirements:** Technical reviewer + Change Advisory Board for production.  
- **Implementation:** Use feature branches, run full validation pipeline, capture plan output for approval.  
- **Post-Change:** Update change log, confirm monitoring coverage, schedule post-implementation review if P1/P2 triggered.  

---
## 7. Runbook Automation Scripts
| Script | Purpose | Execution |
| --- | --- | --- |
| `daily-health-check.sh` | Aggregates CloudWatch alarms, RDS status, ALB target health, backup status. | `./scripts/daily-health-check.sh --profile prod` |
| `weekly-report.sh` | Generates cost, security, and reliability summary (Markdown). | `./scripts/weekly-report.sh --out reports/week-XX.md` |
| `security-audit.sh` | Runs AWS Config, IAM Access Analyzer, `tfsec`. | GitHub Actions (`security-audit` job) or manual |
| `dr-drill.sh` | Simulates region failover, tests RTO/RPO assumptions. | Off-hours monthly |
| `cost-report.sh` | Pulls Cost Explorer data, budgets, rightsizing, stores JSON/CSV. | After FinOps sync |

Scripts require AWS CLI v2, `jq`, and configured profiles. See inline comments for parameters.

---
## 8. Health Checks & KPIs
- **Availability:** ALB healthy host count ≥ desired capacity.  
- **Latency:** p95 response < 300 ms (warning), < 500 ms (critical).  
- **Error Rate:** 5xx < 1% (warning), 5xx ≥ 5% (critical).  
- **Database:** CPU < 70%, connections < 80% of max.  
- **Cost:** Daily spend variance < 10% week-over-week.  

KPIs visualized in Grafana dashboard `AWS-LandingZone-Operations` with drill-down panels.

---
## 9. Access Management
- Use AWS SSO groups `SDE-Prod-ReadOnly`, `SDE-Prod-Deploy`, `SDE-Prod-BreakGlass`.  
- Break-glass credentials sealed in password manager; rotate monthly and log tamper checks.  
- Temporary elevated access via Just-In-Time workflow (ServiceNow integration).  

---
## 10. Backup & Restore
- **RDS:** Automated backups (35-day retention) + manual snapshots prior to major changes. Restore via cross-region read replica script.  
- **S3:** Versioning + MFA delete enabled. Lifecycle rules for infrequent access tiers.  
- **EBS:** Snapshots triggered nightly via Lambda; validated during DR drill.  
- **Verification:** Document restore evidence in monthly DR report.  

---
## 11. Incident Logging
- Incidents tracked in PagerDuty + Jira (`OPS-INC-*`).  
- Each incident must reference relevant playbook section (e.g., `PLAYBOOK-P01-INC-003`).  
- Post-incident review scheduled within 48 hours for P1/P2.  
- Metrics: MTTA, MTTR, incident frequency, SLA/SLO compliance.  

---
## 12. Appendices
- **Appendix A:** Notification templates (Slack/email).  
- **Appendix B:** On-call handoff checklist.  
- **Appendix C:** Links to dashboards, cost explorer saved reports, AWS health RSS feed.  

