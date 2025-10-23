# P02 · IAM Security Hardening — Operations Runbook

> **Audience:** Security engineers and platform operators managing day-to-day IAM guardrails.

---
## 1. Contact Matrix
- **Primary On-Call:** Security Engineering PagerDuty schedule `SEC-IAM-Primary`.
- **Secondary:** Cloud Platform Security Lead (`sec-lead@portfolio.local`).
- **Escalation:** Primary → Secondary → CISO → CTO.

---
## 2. Daily Checklist
| Time (UTC) | Task | Tooling |
| --- | --- | --- |
| 01:00 | Review IAM Access Analyzer findings | AWS Console → IAM → Access Analyzer |
| 05:00 | Inspect GuardDuty findings scoped to IAM anomalies | AWS GuardDuty |
| 09:00 | Validate that break-glass credentials remain sealed | Vault audit log |
| 13:00 | Confirm AWS Config rules `iam-required-mfa` and `iam-policy-blacklist` compliance | AWS Config |
| 17:00 | Reconcile ServiceNow access requests with Identity Center assignments | ServiceNow, AWS SSO |
| 21:00 | Run `scripts/security/scan-cluster.sh` for OPA policy drift | Repository scripts |

Attach evidence for each task to the daily security operations ticket (`SECOPS-<date>`).

---
## 3. Weekly Procedures
- **Monday:** Rotate Security Hub delegated administrator credentials; export latest compliance report.
- **Tuesday:** Execute policy regression tests via `make iam-test` (runs `opa test` + `cfn-lint`).
- **Wednesday:** Perform identity review—list users without MFA, confirm remediation tickets.
- **Thursday:** Re-run Terraform plan for IAM baseline (`projects/p02-iam-hardening/infra`) and capture diff.
- **Friday:** Publish weekly summary (least-privilege progress, unused roles) to `#security-leadership`.

---
## 4. Monthly Procedures
1. Conduct access recertification for privileged roles; disable or rotate stale access keys.
2. Validate automated remediation runbooks (e.g., `iam-disable-stale-keys`) in a sandbox account.
3. Update the IAM architecture diagram if new AWS services were adopted.
4. Audit CloudTrail Lake queries for suspicious activity; export results to the compliance share.
5. Run tabletop exercise covering insider threat and credential compromise scenarios.

---
## 5. Tooling Inventory
| Component | Location | Description |
| --- | --- | --- |
| IAM policy definitions | `projects/p02-iam-hardening/policies/` | JSON policy docs, versioned via Git |
| OPA policies | `projects/p02-iam-hardening/policy-as-code/` | Rego constraints enforcing least privilege |
| Automation scripts | `projects/p02-iam-hardening/scripts/` | CLI utilities for validation and reports |
| Dashboards | Grafana → `Security/IAM` | Real-time metrics (MFA adoption, stale credentials) |

---
## 6. Break-Glass Process
1. On-call engineer opens break-glass request in ServiceNow with incident reference.
2. Security Lead approves request and unlocks credentials in Vault for a 60-minute window.
3. Engineer assumes `BreakGlassAdmin` role via AWS SSO; all actions recorded in CloudTrail.
4. Upon completion, engineer logs summary in incident ticket; Vault automatically rotates secret.

---
## 7. Incident Documentation
- Create Jira ticket (`SEC-INC-###`) for each IAM security incident.
- Reference appropriate playbook section (`PLAYBOOK-P02-INC-*`).
- Capture CloudTrail evidence, Access Analyzer results, and remediation timeline.

---
## 8. Metrics & Reporting
- **MFA Coverage:** Target ≥ 99% of identities.
- **Unused Permissions:** Target ≤ 5% of IAM policies with unused actions in the last 90 days.
- **Break-Glass Usage:** Target zero unplanned activations per quarter.
- **Automated Remediation Success Rate:** Target ≥ 95% for Config/SSM rules.

Metrics surfaced in Grafana panel `Security/IAM/Key Metrics`; alerts configured via Alertmanager for threshold breaches.
