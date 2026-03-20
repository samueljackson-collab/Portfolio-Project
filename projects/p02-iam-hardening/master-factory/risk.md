# Risk Register — P02 IAM Hardening Master Factory

Risks focus on drift from least privilege, unnoticed external access, and stale credentials.

| Risk | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Access Analyzer disabled or misconfigured | External access goes undetected | CI/CD guard requiring successful `make simulate`; observability alert on missing scans | Platform Security |
| MFA enforcement bypassed | Privileged access without MFA | Session policies deny non-MFA; test harness in `make test`; manual checks during releases | IAM Ops |
| Wildcard/overbroad policies merged | Privilege creep and audit findings | Policy linting in `make validate-policies`; mandatory reviewer sign-off; ADR for exceptions | Engineering Leads |
| Unused credentials linger | Increased compromise surface | Scheduled cleanup jobs with reports; `reporting.md` tracks MTTR; automation disables keys | Identity Engineering |
| Policy drift between IaC and runtime | Inconsistent access | `make policy-diff` in pipelines; drift alerts in observability; rollback steps in `operations.md` | Platform SRE |
