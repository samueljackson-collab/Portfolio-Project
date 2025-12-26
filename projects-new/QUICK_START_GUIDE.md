# P-Series Quick Start & Status Guide

**Status:** 🟢 Maintained | **Version:** 2.0.0 | **Last Updated:** 2025-11-13

This guide is the canonical reference for the 20 project (P01–P20) delivery tracks. All active code lives under `projects/pXX-*`. The retired `projects-new/PXX-*` scaffolds have been removed to eliminate duplicate sources of truth.

---
## Table of Contents
1. [Where to Work](#where-to-work)
2. [Baseline Setup](#baseline-setup)
3. [Project Status Checklist](#project-status-checklist)
4. [Common Commands](#common-commands)
5. [Portfolio TODOs](#portfolio-todos)
6. [Troubleshooting](#troubleshooting)

---
## Where to Work
- **Canonical root:** `projects/pXX-project-slug` (example: `projects/p01-aws-infra`).
- Each directory already includes domain-specific READMEs, runbooks, and automation. Use these paths in documentation, scripts, and demos.
- The helper scripts (`scripts/create-projects.sh`, `scripts/validate-projects.sh`) now default to `projects/` so they reinforce the live assets.

---
## Baseline Setup
1. **Install prerequisites**
   - Python 3.9+, Node.js 18+ (for JS projects), Docker 24+, Terraform 1.5+, kubectl 1.27+, AWS CLI v2, and Make.
2. **Choose a project**
   - `cd projects/p01-aws-infra` (replace ID/slug as needed).
3. **Configure environment variables**
   - If `.env.example` exists (now shipped for every P project), copy it: `cp .env.example .env` and edit the values listed in the README. Some manual/QA-only projects describe artifacts instead of env vars—follow the README instructions when `.env.example` is not required.
4. **Install dependencies**
   - `make setup` or `python -m venv .venv && pip install -r requirements.txt -r requirements-dev.txt`.
   - For Node-based suites (`p06`, `p08`), run `npm install` or `pnpm install` as documented.
5. **Run checks**
   - `make test` executes the default suite. Fresh `tests/integration/` and `tests/e2e/` placeholders exist across the P projects so you can gradually add deeper coverage without restructuring.
6. **Deploy / simulate**
   - Use the Makefile targets published in each README (`make deploy-dev`, `make run`, `make scan-all`, etc.).

---
## Project Status Checklist
| ID | Project | Directory | Functional Scope | Next Improvements |
|----|---------|-----------|------------------|-------------------|
| P01 | AWS Infrastructure Automation | `projects/p01-aws-infra` | CloudFormation VPC/RDS stack (`infra/vpc-rds.yaml`) plus DR drill automation (`scripts/dr-drill.sh`). | Add AWS Config/GuardDuty outputs to close remaining roadmap items. |
| P02 | IAM Security Hardening | `projects/p02-iam-hardening` | Least-privilege policy pack (`policies/*.json`), Access Analyzer automation, and policy diff tooling. | Expand automation to remediate unused credentials and wire in Organizations SCP samples. |
| P03 | Hybrid Network Connectivity | `projects/p03-hybrid-network` | WireGuard/IPsec lab with benchmarking scripts (`scripts/test_connectivity.sh`). | Document the planned BGP/SD-WAN scenarios and capture perf traces. |
| P04 | Operational Monitoring Stack | `projects/p04-ops-monitoring` | Prometheus/Grafana/Alertmanager compose bundle plus remediation hooks under `config/`. | Export dashboard JSON + PagerDuty runbooks for evidence. |
| P05 | Mobile App Manual Testing | `projects/p05-mobile-testing` | Test charters, device matrix, regression checklist, and defect samples (`docs/`, `test-cases/`, `defects/`). | Automate smoke checks and attach screenshots/log capture to each charter. |
| P06 | Web App Automated Testing | `projects/p06-e2e-testing` | Playwright end-to-end suite (`playwright.config.ts`, `tests/`) with Make targets for CI. | Stabilize mobile viewport coverage and publish CI artifacts. |
| P07 | International Roaming Simulation | `projects/p07-roaming-simulation` | Python roaming simulator (`src/`, `config/roaming.yaml.example`) and pytest scenarios. | Add metrics export + packet-capture samples for observability evidence. |
| P08 | Backend API Testing | `projects/p08-api-testing` | Postman collections and Newman CLI harness (`collections/`, `tests/`). | Capture JSON schema contracts per endpoint and attach latency baselines. |
| P09 | Cloud-Native POC | `projects/p09-cloud-native-poc` | FastAPI app, Docker assets, and pytest coverage >90%. | Integrate container scan results + k8s manifests for next deployment stage. |
| P10 | Multi-Region Architecture | `projects/p10-multi-region` | Active/passive AWS deployment scripts + failover testing automation. | Record Route 53 health-check screenshots and terraform state outputs. |
| P11 | API Gateway & Serverless | `projects/p11-serverless` | SAM templates, Lambda handlers, DynamoDB data layer, and CloudWatch/X-Ray hooks. | Publish load testing scripts + IAM least-privilege review. |
| P12 | Data Pipeline (Airflow) | `projects/p12-data-pipeline` | Dockerized Airflow stack with ETL DAGs stored under `dags/`. | Add sample dataset snapshots + QA checklist for DAG promotions. |
| P13 | High-Availability Web App | `projects/p13-ha-webapp` | NGINX load balancer, replicated app tier, and DB replication via Docker Compose. | Capture failover drill logs and synthetic monitoring evidence. |
| P14 | Disaster Recovery | `projects/p14-disaster-recovery` | Backup scripts (`scripts/backup_database.sh`, `scripts/dr_drill.py`) and RPO/RTO docs. | Automate artifact uploads (backup logs, restore screenshots) into `docs/`. |
| P15 | Cloud Cost Optimization | `projects/p15-cost-optimization` | Athena CUR queries (`queries/`), FinOps scripts, and dashboards. | Wire in forecasting notebooks + Savings Plan calculator outputs. |
| P16 | Zero-Trust Architecture | `projects/p16-zero-trust` | Policy templates, cert automation, and threat model documentation. | Add live demos of policy evaluation + microsegmentation lab notes. |
| P17 | Terraform Multi-Cloud | `projects/p17-terraform-multicloud` | Shared modules for AWS/Azure plus CI hooks. | Capture backend state configuration details and example workspace outputs. |
| P18 | CI/CD + Kubernetes | `projects/p18-k8s-cicd` | kind-based dev cluster, GitHub Actions workflow, and K8s manifests (`manifests/`). | Add blue/green demo notes and container registry promotion policy. |
| P19 | Cloud Security Automation | `projects/p19-security-automation` | CIS compliance scanner (`scripts/cis_compliance.py`) and remediation playbooks. | Attach sample compliance reports + GuardDuty integration. |
| P20 | Observability Engineering | `projects/p20-observability` | Prometheus/Grafana/Loki configs with dashboard JSON exports (`dashboards/`). | Add trace instrumentation examples and Alertmanager webhook samples. |

---
## Common Commands
```bash
# Bootstrap environment
make setup

# Run default tests
make test

# Run integration/e2e suites (folders created for all P projects)
pytest tests/integration -q
pytest tests/e2e -q

# Deploy, emulate, or scan (project specific)
make deploy-dev
make run
make scan-all
```

---
## Portfolio TODOs
- [ ] Attach screenshots/log evidence for monitoring-heavy projects (P04, P20).
- [ ] Publish GuardDuty/Config automation referenced in P01/P19 roadmaps.
- [ ] Expand CI examples (Playwright + GitHub Actions) for P06 to prove headless stability.
- [ ] Add sample datasets + anonymized records for P12 DAG demonstrations.

---
## Troubleshooting
- **`.env.example` missing?** Every P project now ships one. If yours is custom, regenerate it from the README variable table.
- **Integration folders empty?** They were added intentionally as placeholders—populate them as soon as you have cross-service scenarios.
- **Script path mismatches?** Re-run `scripts/validate-projects.sh` to list missing artifacts per project (it now points at `projects/`).
- **Legacy references to `projects-new/`?** Update links to `projects/pXX-*`; the alternate tree has been retired.
