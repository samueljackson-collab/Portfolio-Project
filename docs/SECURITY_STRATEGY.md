# Security Strategy

## 1. Guiding Principles
- **Zero Trust Everywhere** – Every identity (human and workload) must continuously authenticate, authorize, and encrypt communications. Implicit trust based on network location is eliminated.
- **Shift-Left DevSecOps** – Security is embedded from ideation through operations: IaC scanning, code review checklists, automated compliance testing, and runtime guardrails.
- **Defense-in-Depth** – Layered controls across identity, network, data, application, and recovery domains prevent single points of failure.
- **Auditability & Evidence** – Every control produces verifiable artifacts (logs, dashboards, reports) to satisfy governance, risk, and compliance requirements.

## 2. Identity & Access Management
- **Federated Identity** – AWS IAM Identity Center integrates with corporate IdP; SCIM syncs groups to GitHub, Kubernetes, and internal apps.
- **Role-Based Access Control** – Fine-grained roles (Platform, Data, Security, ReadOnly) map to least-privilege IAM policies and Kubernetes RBAC roles.
- **Just-In-Time Elevation** – Elevated privileges granted via Access Manager workflows with automatic expiration and audit trail.
- **Service Identities** – Workloads use IAM Roles for Service Accounts (IRSA), AWS Lambda execution roles, and workload identities signed via SPIFFE/SPIRE.

## 3. Network Security
- **Segmentation** – AWS VPC architecture isolates public, application, data, and security services subnets. Network ACLs and security groups enforce explicit flows.
- **Secure Edge** – CloudFront + AWS WAF protect static and API workloads; Shield Advanced defends against volumetric attacks.
- **Service Mesh** – Istio (roadmap) enforces mTLS, traffic policy, and rate limiting between services. Until mesh rollout, ingress controllers terminate TLS with ACM certificates.
- **Secure Remote Access** – AWS Client VPN with MFA-protected access; bastion hosts rotate SSH keys nightly via SSM automation.

## 4. Application Security
- **Static Application Security Testing (SAST)** – Bandit, ESLint security plugin, cargo-audit, and semgrep run in CI pipelines.
- **Dependency Governance** – Renovate bot manages dependency updates; SBOM generated via Syft/Grype and stored in artifact repository.
- **Secrets Management** – No secrets in Git. Use AWS Secrets Manager, Parameter Store, or HashiCorp Vault (lab) with auto-rotation and access logging.
- **Policy-as-Code** – OPA Gatekeeper enforces Kubernetes policies. Terraform Sentinel policies ensure infrastructure compliance (encryption, tagging, backups).

## 5. Data Protection
- **Classification & Tagging** – Data assets labeled (Public, Internal, Confidential, Restricted) with automated detection via Macie.
- **Encryption** – All data at rest uses KMS CMKs. In transit, TLS 1.2+ enforced with strict cipher suites. Client apps pin certificates using AWS ACM PCA chain.
- **Backup & Retention** – RDS snapshots, DynamoDB PITR, S3 versioning, and PBS integration for Proxmox/VM workloads. Backups validated monthly via restore drills documented in DR runbooks.
- **Data Loss Prevention** – GuardDuty and Security Hub aggregate anomalies; SNS notifications escalate to SecOps.

## 6. Cloud Governance & Compliance
- **Benchmark Alignment** – Controls mapped to CIS AWS Foundations, NIST CSF, and ISO 27001 Annex A.
- **Continuous Compliance** – AWS Config, Security Hub, and Cloud Custodian enforce guardrails with auto-remediation Lambda functions.
- **Change Management** – Pull requests require security review for sensitive modules. Release trains include threat modeling updates and security test evidence.
- **Incident Response** – Runbooks stored in `projects/strategy/disaster-recovery-plan/runbooks/` define detection, containment, eradication, and recovery steps.

## 7. Supply Chain Security
- **Source Integrity** – Branch protections, signed commits (GPG/SSH), CODEOWNERS, and mandatory reviews.
- **Build Integrity** – GitHub Actions and GitLab CI use OIDC to obtain short-lived tokens. Artifacts signed with Cosign; provenance attestations stored in Rekor.
- **Runtime Integrity** – Container images scanned pre-deploy; Kubernetes uses image policy webhook to enforce signed images only. Lambda layers verified against checksums in Parameter Store.

## 8. Monitoring & Response
- **Telemetry Sources** – CloudTrail, VPC Flow Logs, GuardDuty, Prometheus, Loki, and custom app logs centralize into the monitoring stack.
- **Alerting & Automation** – Critical alerts route to PagerDuty; high-fidelity detections trigger Lambda runbooks for quarantine or IAM policy revocation.
- **Threat Hunting** – Quarterly hunts pivot off aggregated telemetry using Athena/SQL + Jupyter notebooks stored in security project.
- **Tabletop Exercises** – Semi-annual exercises validate DR and IR readiness with business stakeholders.

## 9. Privacy & Data Ethics
- **Data Minimization** – Collect only necessary personal data; anonymize streaming events where possible via PySpark transforms.
- **Governance** – Data retention schedules enforced via lifecycle policies; subject access request workflows documented in governance playbooks.
- **Ethical AI** – AI assistant uses grounded responses with citation requirements, bias evaluation, and manual approval for new data sources.

## 10. Metrics & Continuous Improvement
- **Key Risk Indicators (KRIs)** – MTTR, # of policy violations, patch latency, phishing simulation success rate.
- **Key Performance Indicators (KPIs)** – % infrastructure-as-code coverage, MFA adoption, automated remediation success.
- **Feedback Loop** – Monthly security council reviews metrics, updates roadmap, and assigns action items tracked in Jira/Notion.

