# Security Package

## Principles
- **Least Privilege:** IAM roles scoped to required services; no wildcard admin policies; short-lived credentials.
- **Defense in Depth:** Network segmentation (public/private/db subnets), WAF, SG whitelisting, encryption everywhere.
- **Shift Left:** Security scans and policy checks embedded in CI/CD; secrets never committed; infrastructure policies enforce guardrails.

## Controls
- **Identity & Access**
  - IAM roles for Terraform, ECS tasks, and CI runners with scoped permissions; SSO with MFA; session durations capped.
  - IAM Access Analyzer and GuardDuty enabled; alerts routed to security channel.
- **Secrets Management**
  - AWS Secrets Manager/SSM Parameter Store for DB creds, API keys, TLS cert references.
  - Automatic rotation policies for DB credentials every 90 days; access via task roles only.
- **Network Security**
  - WAF rules for OWASP Top 10, rate limiting, geo-blocking as required.
  - SG rules allow ALB → ECS and ECS → RDS traffic; no inbound DB from internet; egress restricted where feasible.
  - VPC Flow Logs + GuardDuty for anomaly detection with daily review.
- **Data Protection**
  - TLS 1.2+ enforced on ALB and service-to-service calls; ACM-managed certs.
  - KMS encryption for RDS, EBS, S3, and Secrets Manager; backups encrypted and copied cross-region for DR.
- **Pipeline Security**
  - gitleaks/secret scanning; dependency scanning with trivy/grype; container signing (cosign) before deploy.
  - OPA/Conftest policies block risky Terraform patterns (public RDS, open SGs, missing encryption).
  - Required code reviews, branch protections, and signed commits.
- **Logging & Monitoring**
  - Centralized CloudWatch logs; alert on authentication failures, WAF blocks, IAM anomalies.
  - Immutable S3 bucket for audit logs with lifecycle and retention policies; access logged and least privilege enforced.

## Compliance & Governance
- **Standards Alignment:** Maps to CIS AWS Foundations controls and SOC 2-aligned practices for access, change, and monitoring.
- **Evidence:** CI-generated bundles include plan/apply outputs, SBOMs, scans, and approvals (see `CODE-GENERATION-PROMPTS.md`, Variant F).
- **Exceptions:** Documented in risk register with owner, expiry, and compensating controls; reviewed monthly.
- **Reviews:** Quarterly security review; pen tests annually or after major architectural change; tabletop incident drill twice yearly.

## Incident Response
- **Preparation:** Runbooks linked in `OPERATIONS-PACKAGE.md`; on-call rotation documented with escalation tree.
- **Detection:** Alerts for IAM anomalies, WAF spikes, RDS auth failures, unusual outbound traffic, and privileged role use.
- **Containment & Eradication:** Revoke credentials, rotate keys, isolate compromised tasks via security group updates, rebuild images.
- **Recovery:** Re-deploy clean images, restore DB if tampering detected, validate integrity with checksums and audit logs.
- **Post-Incident:** Root cause analysis within 72 hours; update controls, ADRs, and training; track corrective actions.

## Secure SDLC Checklist
- Threat model updates for new features touching data stores or exposure patterns.
- Dependency and container scanning on every PR and nightly; fail on critical issues.
- Secrets redaction in logs; local development guidance avoids real secrets.
- Security peer review required for changes affecting network boundaries, auth, or cryptography.
