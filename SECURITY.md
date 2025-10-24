# Security Posture

Security is embedded throughout the Portfolio API platform. This document outlines the controls, policies, and operational processes that protect the environment. It references artifacts stored in [`security/`](./security/) and monitoring hooks defined in [`monitoring/`](./monitoring/).

## Identity and Access Management

- **AWS Roles:** IAM policies in [`security/policies/iam-portfolio-api.json`](./security/policies/iam-portfolio-api.json) define least-privilege access for Terraform, CI/CD, and runtime workloads.
- **Kubernetes RBAC:** RoleBindings and ClusterRoles are generated from [`infrastructure/kubernetes/rbac/`](./infrastructure/kubernetes/rbac/) templates. Service accounts use IAM Roles for Service Accounts (IRSA).
- **Secrets Handling:** Credentials are stored in AWS Secrets Manager with automatic rotation. External Secrets Operator maps secrets into namespaces with minimal scope.

## Network Security

- **Segmentation:** VPC subnetting isolates ingress, application, and data tiers. Security groups block lateral movement.
- **Kubernetes Network Policies:** See [`security/policies/network-policy.yaml`](./security/policies/network-policy.yaml) for enforced ingress/egress rules.
- **Ingress Protections:** AWS WAF rules filter OWASP Top 10 attacks. Managed rulesets are documented in [`documentation/runbooks/waf-tuning.md`](./documentation/runbooks/waf-tuning.md).

## Supply-Chain Protections

- **Image Signing:** Container images are signed with cosign. Admission controllers validate signatures before scheduling pods.
- **Dependency Scanning:** [`scripts/compliance-scan.sh`](./scripts/compliance-scan.sh) runs Trivy and Syft scans on every build. Reports upload to the security data lake for retention.
- **Provenance:** GitHub Actions uses OIDC to request short-lived credentials. Build metadata is recorded in in-toto attestations stored in S3.

## Data Protection

- **Encryption:** All data at rest uses AWS-managed KMS keys. TLS 1.2+ enforces encryption in transit.
- **Backups:** Documented in [`documentation/runbooks/disaster-recovery.md`](./documentation/runbooks/disaster-recovery.md). Automated tests validate restore procedures quarterly.
- **Data Retention:** Portfolio content retention policies align with privacy requirements outlined in [`security/policies/data-retention.md`](./security/policies/data-retention.md).

## Monitoring & Incident Response

- **Alerting:** Prometheus rules in [`monitoring/prometheus/alerts.yml`](./monitoring/prometheus/alerts.yml) trigger PagerDuty incidents based on latency, error rate, and resource saturation.
- **Logging:** Structured logs stream to OpenSearch with fine-grained access controls. Sensitive fields are redacted at the Fluent Bit layer.
- **Runbooks:** Incident response steps live in [`documentation/runbooks/incident-response.md`](./documentation/runbooks/incident-response.md).

## Compliance Checklist

| Control | Implemented | Reference |
| --- | --- | --- |
| MFA enforced for privileged users | ✅ | [`documentation/onboarding.md`](./documentation/onboarding.md#mfa-setup) |
| Infrastructure drift detection | ✅ | [`scripts/compliance-scan.sh`](./scripts/compliance-scan.sh) |
| Vulnerability scanning | ✅ | [`monitoring/prometheus/alerts.yml`](./monitoring/prometheus/alerts.yml) & build pipeline reports |
| Least privilege IAM | ✅ | [`security/policies/iam-portfolio-api.json`](./security/policies/iam-portfolio-api.json) |
| Encryption at rest & in transit | ✅ | [`documentation/runbooks/disaster-recovery.md`](./documentation/runbooks/disaster-recovery.md#encryption-controls) |

## Access Controls

- Production access is gated behind AWS IAM Identity Center with device posture checks.
- Terraform Cloud workspaces use single-use access tokens rotated every deployment cycle.
- Emergency access break-glass procedures are documented in [`documentation/runbooks/break-glass.md`](./documentation/runbooks/break-glass.md).

## Security Testing

- **Static Analysis:** GolangCI-Lint and Semgrep run on every pull request.
- **Dynamic Testing:** OWASP ZAP integration tests API endpoints nightly; findings triaged via Jira.
- **Penetration Tests:** Annual third-party pentests review architecture, configuration, and custom code. Reports are cataloged in [`documentation/security/pentest-reports/`](./documentation/security/pentest-reports/) with restricted access instructions.

