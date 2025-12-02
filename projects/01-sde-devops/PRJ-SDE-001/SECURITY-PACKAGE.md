# Security Package

## Principles
- **Least Privilege:** IAM roles scoped to required services; no wildcard admin policies.
- **Defense in Depth:** Network segmentation (public/private/db subnets), WAF, SG whitelisting, encryption everywhere.
- **Shift Left:** Security scans and policy checks embedded in CI/CD; secrets never committed.

## Controls
- **Identity & Access:**
  - IAM roles for Terraform, ECS tasks, and CI runners with scoped permissions.
  - SSO for operators; MFA enforced; short-lived session tokens.
- **Secrets Management:**
  - AWS Secrets Manager/SSM Parameter Store for DB creds, API keys, and TLS cert references.
  - Automatic rotation policies for DB credentials every 90 days.
- **Network Security:**
  - WAF rules for common OWASP Top 10; rate limiting and geo-blocking as required.
  - SG rules only allow ALB → ECS and ECS → RDS traffic; no inbound DB from internet.
  - VPC Flow Logs + GuardDuty for anomaly detection.
- **Data Protection:**
  - TLS 1.2+ enforced on ALB and service-to-service calls.
  - KMS encryption for RDS, EBS, S3, and Secrets Manager.
  - Backups encrypted and copied cross-region for DR.
- **Pipeline Security:**
  - gitleaks/secret scanning; dependency scanning with trivy/grype.
  - OPA/Conftest policies to block risky Terraform patterns (public RDS, open SGs).
  - Required code reviews and signed commits.
- **Logging & Monitoring:**
  - Centralized CloudWatch logs; alert on authentication failures and WAF blocks.
  - Immutable S3 bucket for audit logs with lifecycle and retention policies.

## Compliance & Governance
- **Standards Alignment:** Maps to CIS AWS Foundations controls for networking, IAM, logging, and monitoring.
- **Exceptions:** Documented in risk register with owner, expiry, and compensating controls.
- **Reviews:** Quarterly security review; pen tests annually or after major architectural change.

## Incident Response
- **Preparation:** Runbooks linked in `OPERATIONS-PACKAGE.md`; on-call rotation documented.
- **Detection:** Alerts for IAM anomalies, WAF spikes, RDS auth failures, and unusual outbound traffic.
- **Containment & Eradication:** Revoke credentials, rotate keys, isolate compromised tasks via security group updates.
- **Recovery:** Re-deploy clean images, restore DB if tampering detected, validate integrity with checksums.
- **Post-Incident:** Root cause analysis within 72 hours; update controls and ADRs.
