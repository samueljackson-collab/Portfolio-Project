# Original Portfolio Asset Map

This directory links the narrative from the legacy portfolio README to the assets included in this export. Each entry identifies
where to find comparable infrastructure, documentation, or evidence, and flags items that were intentionally excluded.

## Completed Projects

### Homelab & Secure Network Build
- **Export coverage:** The network architecture and access controls are described in [ARCHITECTURE.md](../ARCHITECTURE.md#security-controls) and enforced by Terraform modules under [`infrastructure/terraform/network.tf`](../infrastructure/terraform/network.tf).
- **Operational assets:** Day-two guidance such as break-glass access and WAF tuning is captured in [`documentation/runbooks/`](./runbooks/), and AWS guardrails reside in [`security/policies/`](../security/policies/).
- **Evidence availability:** Physical wiring diagrams and rack photos were not part of this export. Contact the portfolio maintainer for offline review if needed.

### Virtualization & Core Services
- **Export coverage:** Kubernetes manifests for the API, worker, and supporting cronjobs live in [`infrastructure/kubernetes/base/`](../infrastructure/kubernetes/base/), with environment overlays under `overlays/`.
- **Operational assets:** Deployment automation is packaged in [`scripts/deploy.sh`](../scripts/deploy.sh) and database continuity in [`documentation/runbooks/disaster-recovery.md`](./runbooks/disaster-recovery.md).
- **Evidence availability:** Hypervisor screenshots and Proxmox backup logs are out of scope for this export but can be shared privately on request.

### Observability & Backups Stack
- **Export coverage:** Prometheus alerting, dashboards, and recording rules live in [`monitoring/prometheus/`](../monitoring/prometheus/).
- **Operational assets:** [`scripts/smoke-test.sh`](../scripts/smoke-test.sh) exercises health probes, while [`documentation/runbooks/data-validation.md`](./runbooks/data-validation.md) covers catalog integrity checks.
- **Evidence availability:** Grafana exports and incident trend reports remain in the source portfolio repository and are not bundled here.

## Past Projects Requiring Recovery

### Commercial E-commerce & Booking Systems (Rebuild in Progress)
- **Export coverage:** Data quality and recovery processes referenced in the original portfolio map to [`documentation/runbooks/data-retention.md`](./runbooks/data-retention.md) and [`documentation/runbooks/legal-hold.md`](./runbooks/legal-hold.md).
- **Operational assets:** Infrastructure scaffolding for multi-tier web applications is mirrored by the Terraform modules in [`infrastructure/terraform/`](../infrastructure/terraform/).
- **Evidence availability:** Source code and transactional logs remain in archival storage and are intentionally omitted. Stakeholders can coordinate secure access through the maintainer.

## In-Progress Projects (Milestones)

### GitOps Platform with IaC (Terraform + ArgoCD)
- **Export coverage:** Terraform definitions in [`infrastructure/terraform/`](../infrastructure/terraform/) and Kubernetes manifests in [`infrastructure/kubernetes/`](../infrastructure/kubernetes/) reflect the GitOps workflows described in the original roadmap.
- **Operational assets:** [`scripts/deploy.sh`](../scripts/deploy.sh) provides the automation entry point mirrored by the GitOps pipeline.

### AWS Landing Zone (Organizations + SSO)
- **Export coverage:** The bootstrap process for shared services accounts is documented in [`infrastructure/terraform/bootstrap.tf`](../infrastructure/terraform/bootstrap.tf) and the IAM guardrails in [`security/policies/iam-portfolio-api.json`](../security/policies/iam-portfolio-api.json).
- **Operational assets:** [`SECURITY.md`](../SECURITY.md#identity-and-access-management) outlines the identity workflows that back the landing zone implementation.

### Active Directory Design & Automation (DSC/Ansible)
- **Export coverage:** Identity automation patterns are represented through Kubernetes RBAC and IAM integrations detailed in [`infrastructure/kubernetes/rbac/`](../infrastructure/kubernetes/rbac/) and [`SECURITY.md`](../SECURITY.md#identity-and-access-management).
- **Evidence availability:** The original DSC/Ansible playbooks remain proprietary and are excluded from this export.

### Resume Set (SDE/Cloud/QA/Net/Cyber)
- **Export coverage:** The resume collection is not part of this repository. Contact the maintainer for the latest published set.

## Planned Projects (Roadmaps)

### SIEM Pipeline
- **Export coverage:** Alerting and log-forwarding patterns are captured in [`monitoring/prometheus/alerts.yml`](../monitoring/prometheus/alerts.yml) and [`documentation/runbooks/incident-response.md`](./runbooks/incident-response.md).
- **Evidence availability:** SIEM-specific parsers and dashboards are tracked in a private repository pending publication.

### Adversary Emulation
- **Export coverage:** Chaos and resilience testing scenarios in [`documentation/chaos-testing.md`](./chaos-testing.md) provide the operational framework for the emulation roadmap.
- **Evidence availability:** ATT&CK-derived playbooks and tooling remain private until red-team collateral is approved for release.

### Incident Response Playbook
- **Export coverage:** The documented playbook lives in [`documentation/runbooks/incident-response.md`](./runbooks/incident-response.md) with linked post-incident report templates under [`documentation/security/post-incident-reviews/`](./security/post-incident-reviews/).

### Web App Login Test Plan
- **Export coverage:** Not included in this export. Testing artifacts are maintained in a separate QA repository.

### Selenium + PyTest CI
- **Export coverage:** CI/CD scaffolding and smoke test automation are represented by [`scripts/smoke-test.sh`](../scripts/smoke-test.sh) and the GitHub workflow definitions under [`.github/workflows/`](../.github/workflows/).

### Multi-OS Lab
- **Export coverage:** Platform hardening and access policies in [`SECURITY.md`](../SECURITY.md#network-security) represent the security posture applied in the lab environments. Detailed lab automation assets are withheld.

### Document Packaging Pipeline
- **Export coverage:** No automation assets for the packaging pipeline were exported. This remains future work.

### IT Playbook (E2E Lifecycle)
- **Export coverage:** Operational governance is documented through the runbooks in [`documentation/runbooks/`](./runbooks/) and the compliance register at [`documentation/security/compliance-register.md`](./security/compliance-register.md).

### Engineer’s Handbook (Standards/QA Gates)
- **Export coverage:** Quality gates for infrastructure changes are outlined in [`DEPLOYMENT.md`](../DEPLOYMENT.md#continuous-delivery) and the associated GitHub workflows.

## Additional Resources

- **Pentest Reports:** Access procedures for third-party penetration tests are described in [`documentation/security/pentest-reports/README.md`](./security/pentest-reports/README.md).
- **Examples:** API usage samples remain available under [`examples/`](../examples/).

For questions about assets that remain private, reach out via the contact channels listed in the root README.
