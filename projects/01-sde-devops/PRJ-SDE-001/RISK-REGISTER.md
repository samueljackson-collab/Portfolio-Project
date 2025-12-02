# Risk Management Register

| ID | Risk Description | Impact | Likelihood | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Misconfigured security groups exposing services | High | Medium | OPA policies blocking 0.0.0.0/0 on non-ALB SGs; peer review and tfsec in CI | Security Lead | Open |
| R-002 | RDS performance degradation under peak load | High | Medium | Autoscaling storage, performance alarms, read replica option, load tests before releases | DB Engineer | Open |
| R-003 | Terraform state corruption or loss | High | Low | Remote backend with versioning, state locks, backups to cross-region bucket, restricted IAM | Platform Lead | Open |
| R-004 | Dependency vulnerabilities in container images | Medium | High | Nightly trivy scans, base image pinning, rebuild cadence, SBOM publication | App Team | Open |
| R-005 | Inadequate DR readiness leading to extended outage | High | Medium | Quarterly DR drills, documented RTO/RPO, automated restore scripts, cross-region backups | SRE | Open |
| R-006 | Cost overrun due to over-provisioning | Medium | Medium | Terraform cost estimation in CI, rightsizing reviews, autoscaling policies, budget alerts | FinOps | Open |
| R-007 | Logging gaps causing delayed incident triage | Medium | Medium | Structured logging mandate, log schema validation in CI, canary checks, dashboard coverage | Observability Lead | Open |
| R-008 | Credential leakage in repo or logs | High | Low | gitleaks in CI, Secrets Manager usage, redaction filters, incident response plan | Security Lead | Open |

## Review & Governance
- **Cadence:** Monthly risk review; updates after incidents or major changes.
- **Lifecycle:** Risks move Open → Mitigating → Accepted → Closed; updates recorded with date and approver.
- **Alignment:** Each risk maps to controls in `SECURITY-PACKAGE.md` and tests in `TESTING-SUITE.md`.
