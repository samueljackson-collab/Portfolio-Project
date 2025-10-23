# 🔒 Security Overview

## Security Features

### Zero-Trust Architecture
- Mutual TLS between services enforced by Istio
- NetworkPolicies to isolate namespaces and pods
- Identity-aware proxies for API access and management portals

### Data Protection
- Encryption at rest via AWS KMS (S3, RDS, EBS)
- TLS 1.3 enforced for all ingress traffic
- Secrets stored in AWS Secrets Manager / HashiCorp Vault

### Access Control
- RBAC enforced across Kubernetes and AWS IAM
- OAuth2 + JWT authentication for user-facing APIs
- Multi-factor authentication for administrative access

## Compliance

- SOC 2 Type II ready documentation and controls
- GDPR data processing agreements and retention policies
- HIPAA-aligned safeguards for protected health information

Automated scanning uses Trivy, Semgrep, and custom policy-as-code checks defined in `security/compliance/policy-as-code.yaml`.

## Incident Response

| Phase | Description |
| --- | --- |
| Detect | Alertmanager routes actionable notifications to on-call |
| Respond | Runbooks located in project documentation guide remediation |
| Recover | Database migration orchestrator validates integrity before reopening traffic |
| Review | Post-incident reviews tracked with templates in documentation/ |

Security issues can be reported to `security@portfolio.local`. Initial response within 2 hours, mitigation in 24 hours, full resolution within 72 hours.
