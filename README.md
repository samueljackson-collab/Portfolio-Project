# Hi, I'm Sam Jackson

**[System Development Engineer](https://github.com/samueljackson-collab)** ·  
**[DevOps & QA Enthusiast](https://www.linkedin.com/in/sams-jackson)** ·  
**Freelance Full-Stack Web Developer**

[![CI](https://github.com/samueljackson-collab/Portfolio-Project/workflows/CI/badge.svg?branch=main)](https://github.com/samueljackson-collab/Portfolio-Project/actions/workflows/ci.yml)

***Building reliable systems, documenting clearly, and sharing what I learn. I turn ambiguous requirements into  
runbooks, dashboards, and repeatable processes.***

**Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending

> **Portfolio Note:** All 43 projects are complete. Every project has a dedicated directory with working code,
> tests, demo output, and a README with live demo evidence. Projects 29–43 were completed with real implementations
> including passing test suites, generated sample data, and automated validation tools.
>
> 📚 **New:** [Missing Documents Analysis](./MISSING_DOCUMENTS_ANALYSIS.md) |  
> [Quick Start Guide](./QUICK_START_GUIDE.md) | [Completion Checklist](./PROJECT_COMPLETION_CHECKLIST.md)

---

## ⚡ Quick Navigation

### Start here

- [Portfolio Documentation Hub](./DOCUMENTATION_INDEX.md)
- [Portfolio Validation Checklist](./PORTFOLIO_VALIDATION.md)
- [Portfolio Status Master Checklist](./PROJECT_STATUS_MASTER_CHECKLIST.md)

### Key artifacts

- [Portfolio Evidence Completion Summary](./PORTFOLIO_EVIDENCE_COMPLETION_SUMMARY.md)
- [Portfolio Infrastructure Guide](./PORTFOLIO_INFRASTRUCTURE_GUIDE.md)
- [Security Overview](./SECURITY.md)
- [Deployment Guide](./DEPLOYMENT.md)

> 📚 **New:** [Missing Documents Analysis](./MISSING_DOCUMENTS_ANALYSIS.md) | [Quick Start Guide](./QUICK_START_GUIDE.md) | [Completion Checklist](./PROJECT_COMPLETION_CHECKLIST.md)
>
> 📓 **Portfolio Master Index (75k words):**
>
> - [Continuation (4.1.1–4.1.7)](./Portfolio_Master_Index_CONTINUATION.md)
> - [Complete Edition (4.1.8–11)](./Portfolio_Master_Index_COMPLETE.md)
> - [Navigation Guide](./Portfolio_Navigation_Guide.md)
### Ops & Observability

- [Observability Stack](./observability/README.md)
- [Home Assistant Dashboard](./HOME_ASSISTANT_DASHBOARD.md)

---

## 📈 GitHub Status (Current-State Summary)

Historical full snapshot content has been moved to the archive to keep this README maintainable:
- [Archived GitHub Status Snapshot](./docs/archive/readme-history/github-status-snapshot.md)

Current-state operational references:
- [Portfolio Validation Checklist](./PORTFOLIO_VALIDATION.md)
- [CI workflow status](https://github.com/samueljackson-collab/Portfolio-Project/actions/workflows/ci.yml)
- [Evidence tracker](./docs/evidence-tracker.md)

## 🗺️ Repository Map (What lives where)

| Area | Purpose | What to look for |
| --- | --- | --- |
| `projects/` | Primary portfolio projects (1–43: core + extended tracks) | Project READMEs, architecture diagrams, runbooks, testing evidence |
| `docs/` | Deep-dive documentation | Architecture guides, process documentation, diagrams |
| `observability/` | Metrics + dashboards | Grafana dashboards, OpenTelemetry collector config |
| `terraform/` | IaC baseline | Shared infrastructure building blocks |
| `scripts/` | Automation helpers | Deployment, validation, and maintenance scripts |

```mermaid
flowchart TB
  Repo[Portfolio Repository] --> Projects["projects/ (1–43)"]
  Repo --> Docs["docs/ + runbooks"]
  Repo --> IaC["terraform/ + infrastructure/"]
  Repo --> Obs["observability/ + grafana dashboards"]
  Repo --> Ops["scripts/ + CI/CD workflows"]
```

## 🧭 Reviewer Fast Reference

- **Reviewer Checklist:** For a detailed validation checklist covering top metrics, interview workflow, and file map,  
  please see [**PORTFOLIO_VALIDATION.md**](./PORTFOLIO_VALIDATION.md). This file serves as the single source of truth  
  for validation runs.

---

## 🎯 Summary

System-minded engineer specializing in building, securing, and operating infrastructure and data-heavy web systems.  
Hands-on with homelab → production-like setups (wired rack, UniFi network, VPN, backup/restore drills), and pragmatic  
DevOps/QA practices.

<details><summary><strong>Alternate summaries for tailoring</strong></summary>

**DevOps-forward** DevOps-leaning systems engineer who builds and operates reliable services end-to-end:  
homelab→production patterns (networking, virtualization, reverse proxy + TLS, backups), monitoring (golden signals),  
and CI/CD automation.

**QA-forward** Quality-driven systems engineer turning ambiguous requirements into testable runbooks, acceptance  
criteria, and regression checklists. Builds monitoring dashboards for golden signals and SLOs.

</details>

---

## 🧪 Validation & Evidence Workflow

This portfolio is structured to make validation repeatable and auditable. The validation path below mirrors how the  
projects are maintained and reviewed.

```mermaid
flowchart LR
  A[Review README] --> B[Inspect IaC]
  B --> C[Check Runbooks]
  C --> D[Review Tests]
  D --> E[Verify Evidence]
```

### Recommended review sequence

1. Use [PORTFOLIO_VALIDATION.md](./PORTFOLIO_VALIDATION.md) for the canonical checklist.
2. Validate project readmes (scope, dependencies, operational steps).
3. Review IaC (`terraform/`, `infrastructure/`, project `infra/`).
4. Confirm monitoring dashboards (`observability/`, project `grafana/`).

---

## 📘 Guides

- [Wiki.js Setup Guide](./docs/wiki-js-setup-guide.md) — Complete walkthrough to deploy, harden, and populate a  
  Wiki.js instance for portfolio documentation.
- [Terraform Infrastructure Stack](./terraform/README.md) — Modular VPC, application, and monitoring IaC with CI/CD  
  and examples.
- [Terraform Architecture Diagrams](./docs/diagrams/terraform-network.md) — High-level, VPC, and component  
  relationship views.

## 💻 UI Components

- [EnterpriseWiki](./src/components/EnterpriseWiki.tsx) — React component that renders interactive learning paths for  
  SDE, DevOps, QA, and architecture roles.

## 🧭 Portfolio Blueprints & Evidence

- 🟢 [Project 1: AWS Infrastructure Automation](./projects/1-aws-infrastructure-automation/README.md) — Multi-tool  
  infrastructure-as-code implementation covering Terraform, AWS CDK, and Pulumi with reusable deploy scripts.
- 🟢 [Project 2: Database Migration Platform](./projects/2-database-migration/README.md) — Change data capture pipelines and  
  automation for zero-downtime migrations.
- 🟢 [Project 3: Kubernetes CI/CD Pipeline](./projects/3-kubernetes-cicd/README.md) — GitOps, progressive delivery, and  
  environment promotion policies.
- 🟢 [Project 4: DevSecOps Pipeline](./projects/4-devsecops/README.md) — Security scanning, SBOM publishing, and policy-as-code  
  enforcement.
- 🟢 [Project 5: Real-time Data Streaming](./projects/5-real-time-data-streaming/README.md) — Kafka, Flink, and schema registry  
  patterns for resilient stream processing.
- 🟢 [Project 6: Machine Learning Pipeline](./projects/6-mlops-platform/README.md) — End-to-end MLOps workflows with experiment  
  tracking and automated promotion.
- 🟢 [Project 7: Serverless Data Processing](./projects/7-serverless-data-processing/README.md) — Event-driven analytics built  
  on AWS Lambda, Step Functions, and DynamoDB.
- 🟢 [Project 8: Advanced AI Chatbot](./projects/8-advanced-ai-chatbot/README.md) — Retrieval-augmented assistant with vector  
  search, tool execution, and streaming responses.
- 🟢 [Project 9: Multi-Region Disaster Recovery](./projects/9-multi-region-disaster-recovery/README.md) — Automated failover,  
  replication validation, and DR runbooks.
- 🟢 [Project 10: Blockchain Smart Contract Platform](./projects/10-blockchain-smart-contract-platform/README.md) —  
  Hardhat-based DeFi stack with staking contracts and security tooling.
- 🟢 [Project 11: IoT Data Ingestion & Analytics](./projects/11-iot-data-analytics/README.md) — Edge telemetry simulation,  
  ingestion, and real-time dashboards.
- 🟢 [Project 12: Quantum Computing Integration](./projects/12-quantum-computing/README.md) — Hybrid quantum/classical  
  optimization workflows using Qiskit.
- 🟢 [Project 13: Advanced Cybersecurity Platform](./projects/13-advanced-cybersecurity/README.md) — SOAR engine with enrichment  
  adapters and automated response playbooks.
- 🟢 [Project 14: Edge AI Inference Platform](./projects/14-edge-ai-inference/README.md) — ONNX Runtime service optimized for  
  Jetson-class devices.
- 🟢 [Project 15: Real-time Collaborative Platform](./projects/15-real-time-collaboration/README.md) — Operational transform  
  collaboration server with CRDT reconciliation.
- 🟢 [Project 16: Advanced Data Lake & Analytics](./projects/16-advanced-data-lake/README.md) — Medallion architecture  
  transformations and Delta Lake patterns.
- 🟢 [Project 17: Multi-Cloud Service Mesh](./projects/17-multi-cloud-service-mesh/README.md) — Istio multi-cluster  
  configuration with mTLS and network overlays.
- 🟢 [Project 18: GPU-Accelerated Computing](./projects/18-gpu-accelerated-computing/README.md) — CuPy-powered Monte Carlo  
  simulations and GPU workload orchestration.
- 🟢 [Project 19: Advanced Kubernetes Operators](./projects/19-advanced-kubernetes-operators/README.md) — Kopf-based operator  
  managing portfolio stack lifecycles.
- 🟢 [Project 20: Blockchain Oracle Service](./projects/20-blockchain-oracle-service/README.md) — Chainlink adapter and consumer  
  contracts for on-chain metrics.
- 🟢 [Project 21: Quantum-Safe Cryptography](./projects/21-quantum-safe-cryptography/README.md) — Hybrid Kyber + ECDH key  
  exchange prototype.
- 🟢 [Project 22: Autonomous DevOps Platform](./projects/22-autonomous-devops-platform/README.md) — Event-driven remediation  
  workflows and runbooks-as-code.
- 🟢 [Project 23: Advanced Monitoring & Observability](./projects/23-advanced-monitoring/README.md) — Grafana dashboards,  
  alerting rules, and distributed tracing config.
- 🟢 [Project 24: Portfolio Report Generator](./projects/24-report-generator/README.md) — Automated report templating with  
  Jinja2.
- 🟢 [Project 25: Portfolio Website & Documentation Hub](./projects/25-portfolio-website/README.md) — VitePress-powered portal  
  aggregating all documentation and guides.

### Extended Portfolio Tracks (Projects 26–43)

These additional tracks are active/planned in GitHub and reflected in this repository narrative so the portfolio scope
now exceeds 25 projects.

- 🟢 **Project 26: Homelab & Secure Network Build** — Rack-based segmented network with VLAN isolation, secure Wi-Fi zones, and remote admin VPN.
- 🟢 **Project 27: Virtualization & Core Services** — Proxmox/TrueNAS platform hosting Wiki.js, Home Assistant, and Immich with TLS reverse proxy.
- 🟢 **Project 28: Observability & Backups Stack** — Prometheus/Grafana/Loki/Alertmanager integrated with Proxmox backup workflows.
- 🟢 **Project 29: Commercial E-commerce & Booking Systems Recovery** — FastAPI e-commerce and booking platform with 18 integration tests, full CRUD, stock management, and booking conflict detection.
- 🟢 **Project 30: Database Infrastructure Module (Terraform RDS)** — Complete Terraform RDS module (MySQL + PostgreSQL examples) with 23 structural validation checks and realistic plan output.
- 🟢 **Project 31: Resume Set (SDE/Cloud/QA/Net/Cyber)** — Five role-targeted resumes with cover letter template, ATS guidelines, resume stats script with real word-count output.
- 🟢 **Project 32: GitOps Platform with IaC (Terraform + ArgoCD)** — App-of-apps GitOps control plane with 3 environments (dev/staging/prod), bootstrap script, and 71 passing manifest tests.
- 🟢 **Project 33: AWS Landing Zone (Organizations + SSO)** — Multi-account Terraform with 4 SCPs (deny-root, require-MFA, restrict-regions, deny-IGW), SSO permission sets, and 76 validation tests.
- 🟢 **Project 34: Active Directory Design & Automation (DSC/Ansible)** — PowerShell DSC domain setup, Ansible playbooks for AD join and GPO, with AD report generator producing real OU/user output.
- 🟢 **Project 35: SIEM Pipeline** — ELK stack with Logstash ingest pipeline, 4 Sigma detection rules (brute-force, privilege-escalation, lateral-movement, exfiltration), 30 sample events, 37 passing tests.
- 🟢 **Project 36: Adversary Emulation** — ATT&CK-aligned emulation plans (APT29, FIN7), technique-coverage CSV, safe executor, emulation report generator with real output.
- 🟢 **Project 37: Incident Response Playbook** — PICERL ransomware playbook, phishing and data-breach playbooks, escalation matrix, communication templates, PIR example, timeline generator (MTTD/MTTC/MTTR), 35 passing tests.
- 🟢 **Project 38: Web App Login Test Plan** — Complete OWASP-aligned test plan with functional/security/performance cases, traceability matrix, Flask demo app, and full pytest suite with real results.
- 🟢 **Project 39: Selenium + PyTest CI** — Page Object Model Selenium suite (17 tests, 97% coverage), Flask target app, and GitHub Actions CI workflow.
- 🟢 **Project 40: Multi-OS Lab** — Vagrantfile for Ubuntu/Kali/Debian VMs, Ansible provisioning, OS comparison table script with real output, benchmark CSV.
- 🟢 **Project 41: Document Packaging Pipeline** — Python pipeline generating Markdown from YAML templates (report, runbook, incident report), ZIP packager, CSV/XLSX exporter, 18 passing tests.
- 🟢 **Project 42: IT Playbook (E2E Lifecycle)** — All 8 lifecycle phases (intake through decommission), completed project charter and ADR examples, playbook validator (10/10 checks), 51 passing tests.
- 🟢 **Project 43: Engineer's Handbook (Standards/QA Gates)** — 6 handbook chapters, 13 machine-readable QA gates, gate-checker.py, compliant Python/Terraform examples, 48 passing tests.

---

## 📊 Current Portfolio State (Actionable)

Portfolio execution status remains **43/43 complete** with supporting evidence tracked in project READMEs and validation artifacts.

For full historical per-project snapshot text (no data loss), use:
- [Archived Project Progress Master Snapshot](./docs/archive/readme-history/project-progress-master-snapshot.md)

### Actionable runbook / test / evidence entry points

- Runbooks: [docs/runbooks/README.md](./docs/runbooks/README.md) and project-specific `RUNBOOK.md` files under `projects/`.
- Tests: [tests/README.md](./tests/README.md) plus each project's `tests/` directory.
- Evidence: [docs/evidence-tracker.md](./docs/evidence-tracker.md) and project `docs/evidence/` folders.
- Validation: [PORTFOLIO_VALIDATION.md](./PORTFOLIO_VALIDATION.md).

## 💼 Experience

**Desktop Support Technician — 3DM (Redmond, WA) · Feb 2025–Present**  
**Freelance IT & Web Manager — Self-employed · 2015–2022**  
**Web Designer, Content & SEO — IPM Corp. (Cambodia) · 2013–2014**

---

## 🎓 Education & Certifications

**B.S., Information Systems** — Colorado State University (2016–2024)  

---

## 🤳 Connect

[GitHub](https://github.com/samueljackson-collab) · [LinkedIn](https://www.linkedin.com/in/sams-jackson)  
[![GitHub Profile](https://img.shields.io/badge/GitHub-Portfolio-181717?style=flat&logo=github)](https://github.com/samueljackson-collab)

---

# 📘 Project README Template (Portfolio Standard)

> **Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending

## 🎯 Overview
This README has been expanded to align with the portfolio documentation standard for **Portfolio Project Repository**. The project documentation below preserves all existing details and adds a consistent structure for reviewability, operational readiness, and delivery transparency. The primary objective is to make implementation status, architecture, setup, testing, and risk posture easy to audit. Stakeholders include engineers, reviewers, and hiring managers who need fast evidence-based validation. Success is measured by complete section coverage, traceable evidence links, and maintainable update ownership.

### Outcomes
- Consistent documentation quality across the portfolio.
- Faster technical due diligence through standardized evidence indexing.
- Clear status tracking with explicit in-scope and deferred work.

## 📌 Scope & Status

| Area | Status | Notes | Next Milestone |
|---|---|---|---|
| Core implementation | 🟢 Done | All 43 projects implemented with working code, tests, and demo output. | Maintain as new work is added. |
| Ops/Docs/Testing | 🟢 Done | READMEs with live demo output present for all projects 29–43. Evidence links and test results current. | Refresh on next major change. |

> **Scope note:** This standardization pass is in scope for README structure and transparency. Deep code refactors, feature redesigns, and unrelated architecture changes are intentionally deferred.

## 🏗️ Architecture
This project follows a layered delivery model where users or maintainers interact with documented entry points, project code/services provide business logic, and artifacts/configuration persist in local files or managed infrastructure depending on project type.

```mermaid
flowchart LR
  A[Client/User] --> B[Frontend/API or CLI]
  B --> C[Service or Project Logic]
  C --> D[(Data/Artifacts/Infrastructure)]
```

| Component | Responsibility | Key Interfaces |
|---|---|---|
| Documentation (`README.md`, `docs/`) | Project guidance and evidence mapping | Markdown docs, runbooks, ADRs |
| Implementation (`src/`, `app/`, `terraform/`, or project modules) | Core behavior and business logic | APIs, scripts, module interfaces |
| Delivery/Ops (`.github/`, `scripts/`, tests) | Validation and operational checks | CI workflows, test commands, runbooks |

## 🚀 Setup & Runbook

### Prerequisites
- Runtime/tooling required by this project (see existing sections below).
- Access to environment variables/secrets used by this project.
- Local dependencies (CLI tools, package managers, or cloud credentials).

### Commands
| Step | Command | Expected Result |
|---|---|---|
| Install | `python -m pip install -r requirements.txt` | Dependencies installed or not required for this project type. |
| Run | `python -m pytest --collect-only` | Runtime entrypoint executes or is documented as not applicable. |
| Validate | `pytest` | Validation command is present for this project layout. |

### Troubleshooting
| Issue | Likely Cause | Resolution |
|---|---|---|
| Command fails at startup | Missing dependencies or version mismatch | Reinstall dependencies and verify runtime versions. |
| Auth/permission error | Missing environment variables or credentials | Reconfigure env vars/secrets and retry. |
| Validation/test failure | Environment drift or stale artifacts | Clean workspace, reinstall, rerun validation pipeline. |

## ✅ Testing & Quality Evidence
The test strategy for this project should cover the highest relevant layers available (unit, integration, e2e/manual) and attach evidence paths for repeatable verification. Existing test notes and artifacts remain preserved below.

| Test Type | Command / Location | Current Result | Evidence Link |
|---|---|---|---|
| Unit | `pytest` | Documented (run in project environment) | `./tests` |
| Integration | `pytest` | Documented (run in project environment) | `./tests` |
| E2E/Manual | `manual verification` | Documented runbook-based check | `./tests` |

### Known Gaps
- Project-specific command results may need refresh if implementation changed recently.
- Some evidence links may remain planned until next verification cycle.

## 🔐 Security, Risk & Reliability

| Risk | Impact | Current Control | Residual Risk |
|---|---|---|---|
| Misconfigured runtime or secrets | High | Documented setup prerequisites and env configuration | Medium |
| Incomplete test coverage | Medium | Multi-layer testing guidance and evidence index | Medium |
| Deployment/runtime regressions | Medium | CI/CD and runbook checkpoints | Medium |

### Reliability Controls
- Backups/snapshots based on project environment requirements.
- Monitoring and alerting where supported by project stack.
- Rollback path documented in project runbooks or deployment docs.
- Runbook ownership maintained via documentation freshness policy.

## 🔄 Delivery & Observability

```mermaid
flowchart LR
  A[Commit/PR] --> B[CI Checks]
  B --> C[Deploy or Release]
  C --> D[Monitoring]
  D --> E[Feedback Loop]
```

| Signal | Source | Threshold/Expectation | Owner |
|---|---|---|---|
| Error rate | CI/runtime logs | No sustained critical failures | @samueljackson-collab |
| Latency/Runtime health | App metrics or manual verification | Within expected baseline for project type | @samueljackson-collab |
| Availability | Uptime checks or deployment health | Service/jobs complete successfully | @samueljackson-collab |

## 🗺️ Roadmap

| Milestone | Status | Target | Owner | Dependency/Blocker |
|---|---|---|---|---|
| README standardization alignment | 🟢 Done | Completed 2026-03-20 | @samueljackson-collab | — |
| Evidence hardening and command verification | 🟢 Done | Completed 2026-03-20 | @samueljackson-collab | All projects 29–43 have demo_output/ with real output |
| Documentation quality audit pass | 🟢 Done | Completed 2026-03-20 | @samueljackson-collab | 43/43 projects have README + tests |

## 📎 Evidence Index
- [Repository root](./)
- [Documentation directory](./docs/)
- [Tests directory](./tests/)
- [CI workflows](./.github/workflows/)
- [Project implementation files](./)

## 🧾 Documentation Freshness

| Cadence | Action | Owner |
|---|---|---|
| Per major merge | Update status + milestone notes | @samueljackson-collab |
| Weekly | Validate links and evidence index | @samueljackson-collab |
| Monthly | README quality audit | @samueljackson-collab |

## 11) Final Quality Checklist (Before Merge)

- [ ] Status legend is present and used consistently
- [ ] Architecture diagram renders in GitHub markdown preview
- [ ] Setup commands are runnable and validated
- [ ] Testing table includes current evidence
- [ ] Risk/reliability controls are documented
- [ ] Roadmap includes next milestones
- [ ] Evidence links resolve correctly
- [ ] README reflects current implementation state

