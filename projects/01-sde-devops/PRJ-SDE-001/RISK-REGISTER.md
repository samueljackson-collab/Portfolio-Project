# Risk Management Register

| ID | Risk Description | Impact | Likelihood | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Misconfigured security groups exposing services | High | Medium | OPA policies blocking 0.0.0.0/0 on non-ALB SGs; tfsec in CI; quarterly rules review | Security Lead | Mitigating |
| R-002 | RDS performance degradation under peak load | High | Medium | Autoscaling storage, performance alarms, read replica option, load tests before releases | DB Engineer | Mitigating |
| R-003 | Terraform state corruption or loss | High | Low | Remote backend with versioning, state locks, backups to cross-region bucket, restricted IAM; periodic restore tests | Platform Lead | Mitigating |
| R-004 | Dependency vulnerabilities in container images | Medium | High | Nightly trivy scans, base image pinning, rebuild cadence, SBOM publication; SLA: critical in 48h | App Team | Open |
| R-005 | Inadequate DR readiness leading to extended outage | High | Medium | Quarterly DR drills, documented RTO/RPO, automated restore scripts, cross-region backups | SRE | Mitigating |
| R-006 | Cost overrun due to over-provisioning | Medium | Medium | Terraform cost estimation in CI, rightsizing reviews, autoscaling policies, budget alerts, tagging for chargeback | FinOps | Open |
| R-007 | Logging gaps causing delayed incident triage | Medium | Medium | Structured logging mandate, schema validation in CI, canary checks, dashboard coverage; log retention verified quarterly | Observability Lead | Open |
| R-008 | Credential leakage in repo or logs | High | Low | gitleaks in CI, Secrets Manager usage, redaction filters, incident response plan, short-lived tokens | Security Lead | Open |
| R-009 | Compliance evidence incomplete for audits | Medium | Low | Automated evidence bundling from CI (`CODE-GENERATION-PROMPTS` variant F), quarterly audit drills | Compliance | Planned |
| R-010 | Single-AZ dependency through misconfigured subnets | High | Low | Terraform policies enforce multi-AZ; integration tests validate subnet counts; change review checklist | Platform Lead | Mitigating |

## Review & Governance
- **Cadence:** Monthly risk review; updates after incidents or major changes.
- **Lifecycle:** Risks move Open → Mitigating → Accepted → Closed; updates recorded with date and approver.
- **Alignment:** Each risk maps to controls in `SECURITY-PACKAGE.md`, tests in `TESTING-SUITE.md`, and reports in `REPORTING-PACKAGE.md`.
