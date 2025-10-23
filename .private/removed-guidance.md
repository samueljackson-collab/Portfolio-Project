# Removed Guidance Notes

This file retains planning guidance that was removed from public-facing documentation.

## projects/p02-iam-hardening/README.md
### Former "Workstreams"
1. **Access Baselines:** Define permission sets and role boundaries, enforce via Terraform + OPA.
2. **Policy Testing:** Build unit tests with `conftest` for IAM JSON documents.
3. **Continuous Compliance:** Integrate AWS Config + Access Analyzer into CI; failing checks block merges.
4. **Lifecycle Automation:** JIT access workflows, automated break-glass rotation, and Slack notifications.

### Former "Next Deliverables"
- Complete OPA policy library (`iam/opa/`).
- Ship runbook/playbook with escalation paths and audit evidence templates.
- Add GitHub Actions workflow for policy validation and drift detection.

## projects/p02-iam-hardening/docs/RUNBOOK.md
Detailed plan previously noted:
1. Contact & Escalation Matrix.
2. Daily/Weekly/Monthly access hygiene tasks.
3. Change management for permission set updates.
4. Break-glass credential rotation workflows.
5. Compliance evidence gathering checklist.

## projects/p02-iam-hardening/docs/PLAYBOOK.md
- Cover IAM-specific scenarios such as credential compromise, privilege escalation, unused access discovery, and policy violations, including severity definitions, detection triggers, response steps, communication templates, and remediation guidance.

## projects/p09-fullstack-app/README.md
Implementation checklist items:
- [ ] Define API schema and OpenAPI documentation.
- [ ] Build FastAPI service with modular routers, SQLAlchemy models, and async tasks.
- [ ] Create React SPA with authenticated dashboard and responsive layout.
- [ ] Author unit/integration/e2e tests (pytest, React Testing Library, Playwright).
- [ ] Provision infrastructure (ECS, RDS, S3, CloudFront) via Terraform modules shared with P01.
- [ ] Configure CI/CD with GitHub Actions (lint, test, build, deploy).

## projects/p09-fullstack-app/docs/RUNBOOK.md
Pending sections list:
1. On-call rotation, paging policies, and dashboards.
2. Daily checks for API availability, queue depth, and deployment pipelines.
3. Weekly DB maintenance (vacuum analyze, index review) and error budget reports.
4. Deployment process with blue/green validation checklist.
5. Backup/restore drills and data retention policies.

## projects/p09-fullstack-app/docs/PLAYBOOK.md
Planned scenarios:
- API latency spikes and rate limiting misconfiguration.
- Authentication failures (JWT signing key rotation, refresh token storms).
- Deployment rollback due to schema mismatch.
- Queue backlog / worker outage.
- External dependency outage (Stripe, email provider).

## projects/p18-homelab/README.md
Next steps previously listed:
1. Finalize hardware BOM and wiring diagrams.
2. Automate Proxmox provisioning with Ansible + Terraform.
3. Capture before/after metrics for power consumption and network throughput.
4. Document service catalog and dependencies.

## projects/p18-homelab/docs/HANDBOOK.md
Original outline:
1. Objectives & success metrics.
2. Physical topology and rack layout diagrams.
3. Network segmentation plan (VLANs, firewall rules, VPN).
4. Virtualization strategy (Proxmox cluster, storage replication).
5. Service catalog with dependencies and SLAs.
6. Backup, observability, and automation roadmap.

## projects/p18-homelab/docs/RUNBOOK.md
- Daily health checks, backup verification, firmware patch cycles, and service restart procedures for the homelab stack.

## projects/p18-homelab/docs/PLAYBOOK.md
- Incident coverage for power loss, hypervisor failure, storage pool degradation, and VPN outages with enterprise-aligned response flows.

## projects/p20-observability/README.md
Upcoming work items:
1. Finalize Kubernetes-based deployment with Helm charts.
2. Instrument sample services (FastAPI + EC2) for end-to-end telemetry.
3. Automate SLO calculations and error budget tracking.
4. Publish dashboard JSON templates and runbooks.

## projects/p20-observability/docs/HANDBOOK.md
Key sections earmarked for expansion:
1. Observability principles and target SLIs/SLOs.
2. Reference deployments (Kubernetes, Docker Compose, AWS Managed).
3. Telemetry data flow diagrams and storage sizing guidance.
4. Security controls (RBAC, secret management, network policies).
5. Cost optimization (retention, compression, tiered storage).

## projects/p20-observability/docs/RUNBOOK.md
- Runbooks for Prometheus scraping issues, Loki ingestion backpressure, Grafana dashboard governance, and alert routing maintenance.

## projects/p20-observability/docs/PLAYBOOK.md
- Incident coverage for alert storms, data gaps, scaling limits, and telemetry ingestion failures with triage checklists and remediation steps.
