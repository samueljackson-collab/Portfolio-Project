# Security

## Controls
- Enforce AWS Config recorder and GuardDuty in all regions used by the stack.
- ALB behind AWS WAF with managed rules: SQLi, XSS, IP reputation.
- RDS encryption at rest with KMS; enforce TLS in transit.
- IAM: least privilege for CI/CD roles; use IAM roles for service access (no static creds).

## Scanning
- `checkov` and `tfsec` in CI to block insecure resources.
- AWS Inspector/Config conformance packs for CIS foundations.

## Secrets Management
- Store database credentials in Secrets Manager; rotate every 30 days.
- CI/CD pulls secrets via OIDC + scoped IAM role.

## Audit
- Enable CloudTrail with log integrity validation.
- Ship WAF/ALB logs to centralized S3 with lifecycle + access logging.
