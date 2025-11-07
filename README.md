# Hi, I'm Sam Jackson!
**[System Development Engineer](https://github.com/samueljackson-collab)** · **[DevOps & QA Enthusiast](https://www.linkedin.com/in/sams-jackson)** · **Freelance Full-Stack Web Developer**

[![CI](https://github.com/samueljackson-collab/Portfolio-Project/workflows/CI/badge.svg?branch=main)](https://github.com/samueljackson-collab/Portfolio-Project/actions/workflows/ci.yml)

***Building reliable systems, documenting clearly, and sharing what I learn. I turn ambiguous requirements into runbooks, dashboards, and repeatable processes.***

**Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending

> **Portfolio Note:** This repository showcases 25+ portfolio projects spanning Infrastructure as Code, MLOps, cloud platforms, and advanced technologies. Projects marked 🟢 are technically complete with documentation/evidence being prepared (📝). Projects marked 🔵 are planned roadmap items, and 🔄 indicates recovery/rebuild efforts are underway.

> **New:** [📚 Enterprise Wiki Documentation](./wiki/) | [🚀 Wiki.js Setup Guide](./docs/wiki-js-setup-guide.md) | [🎓 Interactive Learning Paths](./enterprise-wiki-app/)

> **Quick Links:** [Missing Documents Analysis](./MISSING_DOCUMENTS_ANALYSIS.md) | [Quick Start Guide](./QUICK_START_GUIDE.md) | [Completion Checklist](./PROJECT_COMPLETION_CHECKLIST.md)

---
## 🎯 Summary
System-minded engineer specializing in building, securing, and operating infrastructure and data-heavy systems. Hands-on with homelab → production-like setups (wired rack, UniFi network, VPN, backup/restore drills), and pragmatic DevOps/QA practices. Portfolio demonstrates expertise across infrastructure automation, observability, MLOps, and operational excellence with comprehensive runbooks, playbooks, and handbooks.

<details><summary><strong>Alternate summaries for tailoring</strong></summary>

**DevOps-forward** DevOps-leaning systems engineer who builds and operates reliable services end-to-end: homelab→production patterns (networking, virtualization, reverse proxy + TLS, backups), monitoring (golden signals), IaC automation with Terraform/CDK/Pulumi, and GitOps workflows with ArgoCD/Flux.

**QA-forward** Quality-driven systems engineer turning ambiguous requirements into testable runbooks, acceptance criteria, and regression checklists. Builds monitoring dashboards for golden signals and SLOs, with comprehensive testing frameworks spanning unit, integration, and E2E testing.

**SRE-forward** Reliability-focused engineer implementing SRE practices: error budgets, SLI/SLO definitions, comprehensive observability stacks (Prometheus/Grafana/Loki), disaster recovery playbooks (RTO: 4-8hrs, RPO: 24-48hrs), and automated incident response procedures.
</details>

---
## 🛠️ Core Skills
- **Infrastructure as Code:** Terraform, AWS CDK, Pulumi, CloudFormation, Ansible, GitOps (ArgoCD, Flux)
- **Cloud Platforms:** AWS (VPC, RDS, ECS, EKS, Lambda, Step Functions), Azure, GCP, multi-region architectures
- **Container & Orchestration:** Docker, Kubernetes, Helm, service mesh (Istio, Linkerd), container security
- **Systems & Infra:** Linux/Windows, networking, VLANs, VPN, UniFi, NAS, Active Directory, pfSense
- **Virtualization/Services:** Proxmox/TrueNAS, reverse proxy + TLS, RBAC/MFA, backup/restore drills
- **Observability & Reliability:** Prometheus, Grafana, Loki, Alertmanager, Jaeger, golden signals, SLOs, PBS
- **CI/CD & Automation:** GitHub Actions, GitLab CI, Jenkins, Argo Workflows, PowerShell, Bash, Python
- **Data Engineering:** PostgreSQL, MySQL, ETL pipelines, data migration, schema design, large-catalog data ops
- **MLOps & AI:** MLflow, Optuna, model serving, experiment tracking, feature stores, ML pipelines
- **Security:** SIEM (Wazuh), IPS/IDS (Suricata), vulnerability scanning, security hardening, compliance
- **Web & Data:** WordPress, e-commerce/booking systems, React, TypeScript, API design
- **Quality & Process:** Runbooks, playbooks, handbooks, acceptance criteria, regression testing, change control

---
## 🟢 Completed Projects (📝 Documentation in Progress)

### Homelab & Secure Network Build
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Designed and wired a home network from scratch: rack-mounted gear, VLAN segmentation, and secure Wi-Fi for isolated IoT, guest, and trusted networks.
**Links**: [Project README](./projects/06-homelab/PRJ-HOME-001/) · [Evidence/Diagrams](./projects/06-homelab/PRJ-HOME-001/assets) *(being prepared)*

### Virtualization & Core Services
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Proxmox/TrueNAS host running Wiki.js, Home Assistant, and Immich behind a reverse proxy with TLS.
**Links**: [Project README](./projects/06-homelab/PRJ-HOME-002/) · [Backup Logs](./projects/06-homelab/PRJ-HOME-002/assets) *(being prepared)*

### Observability & Backups Stack
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Monitoring/alerting stack using Prometheus, Grafana, Loki, and Alertmanager, integrated with Proxmox Backup Server.
**Links**: [Project README](./projects/01-sde-devops/PRJ-SDE-002/) · [Dashboards](./projects/01-sde-devops/PRJ-SDE-002/assets)

---
## 🔄 Past Projects Requiring Recovery

Older commercial efforts live in cold storage while I recreate code, processes, and documentation that were lost when a retired workstation took the original knowledge base with it. Fresh assets will be published as they’re rebuilt.

### Commercial E-commerce & Booking Systems (Rebuild in Progress)
**Status:** 🔄 Recovery in progress
**Description** Previously built and managed: resort booking site; high-SKU flooring store; tours site with complex variations. Code and process docs are being rebuilt for publication.
**Links**: [Project README & Recovery Plan](./projects/08-web-data/PRJ-WEB-001/) · [Evidence](./projects/08-web-data/PRJ-WEB-001/assets) *(pending recovery)*

> **Recovery plan & timeline:** Catalog and restore SQL workflows and automation scripts (Week 1), re-document content management processes and deployment steps (Week 2), publish refreshed artifacts (Week 3+).

---
## 🟠 In-Progress Projects (Milestones)
- **Database Infrastructure Module (Terraform RDS)** · [Project README](./projects/01-sde-devops/PRJ-SDE-001/) · ✅ Module complete, expanding to full-stack
- **Resume Set (SDE/Cloud/QA/Net/Cyber)** · [Project README](./professional/resume/) · 📝 Structure created, content in progress

### 🔵 Planned Infrastructure Projects
- **GitOps Platform with IaC (Terraform + ArgoCD)** · *Roadmap defined*
- **AWS Landing Zone (Organizations + SSO)** · *Research phase*
- **Active Directory Design & Automation (DSC/Ansible)** · *Planning phase*

---
## 🔵 Planned Projects (Roadmaps)

### Cybersecurity Projects
- **SIEM Pipeline**: Sysmon → Ingest → Detections → Dashboards · *Blue team defense*
- **Adversary Emulation**: Validate detections via safe ATT&CK TTP emulation · *Purple team testing*
- **Incident Response Playbook**: Clear IR guidance for ransomware · *Operations readiness*

### QA & Testing Projects
- **Web App Login Test Plan**: Functional, security, and performance test design · *Test strategy*
- **Selenium + PyTest CI**: Automate UI sanity runs in GitHub Actions · *Test automation*

### Infrastructure Expansion
- **Multi-OS Lab**: Kali, SlackoPuppy, Ubuntu lab for comparative analysis · *Homelab expansion*

### Automation & Tooling
- **Document Packaging Pipeline**: One-click generation of Docs/PDFs/XLSX from prompts · *Documentation automation*

### Process Documentation
- **IT Playbook (E2E Lifecycle)**: Unifying playbook from intake to operations · *Operational excellence*
- **Engineer's Handbook (Standards/QA Gates)**: Practical standards and quality bars · *Quality framework*

---
## 📚 Portfolio Projects

This portfolio demonstrates expertise across 25+ comprehensive projects spanning infrastructure automation, cloud platforms, data engineering, MLOps, and advanced technologies. Each project includes implementation guides, operational runbooks, and best practices documentation.

### Infrastructure as Code & Cloud Platforms

#### [Project 1: AWS Infrastructure Automation](./projects/1-aws-infrastructure-automation/)
**Status:** 🔵 Planned · **Tech:** Terraform, AWS CDK, Pulumi
Multi-tool IaC implementation showcasing three approaches to AWS infrastructure management: Terraform modules (VPC, RDS, ECS), AWS CDK stacks (TypeScript), and Pulumi programs (Python). Includes GitOps workflow with Terraform Cloud and comprehensive state management.

**Key Features:**
- Production-grade Terraform modules with validation and testing
- AWS CDK constructs for rapid prototyping and deployment
- Pulumi for policy-as-code and advanced automation
- Multi-account AWS Organizations setup with SSO
- Cost allocation tags and budget alerts

[View Project →](./projects/1-aws-infrastructure-automation/)

---

#### [Project 3: Kubernetes CI/CD Pipeline](./projects/3-kubernetes-cicd-pipeline/)
**Status:** 🔵 Planned · **Tech:** Kubernetes, ArgoCD, GitLab CI, Helm
Production-ready GitOps pipeline with ArgoCD managing deployments across dev/staging/prod clusters. Includes progressive delivery with Argo Rollouts, automated rollback, and comprehensive observability.

**Key Features:**
- Multi-cluster ArgoCD setup with ApplicationSets
- Progressive delivery with canary and blue-green strategies
- Automated secret management with External Secrets Operator
- Policy enforcement with OPA Gatekeeper
- Cost optimization with Goldilocks and VPA

[View Project →](./projects/3-kubernetes-cicd-pipeline/)

---

#### [Project 11: Multi-Cloud Cost Optimization Platform](./projects/11-multi-cloud-cost-optimization/)
**Status:** 🔵 Planned · **Tech:** Python, AWS Cost Explorer, Azure Cost Management
Automated cost analysis and optimization recommendations across AWS, Azure, and GCP. Identifies underutilized resources, recommends rightsizing, and implements automated shutdown schedules.

[View Project →](./projects/11-multi-cloud-cost-optimization/)

---

#### [Project 14: Service Mesh Implementation (Istio/Linkerd)](./projects/14-service-mesh-implementation/)
**Status:** 🔵 Planned · **Tech:** Istio, Linkerd, Kubernetes, Kiali
Production service mesh deployment with traffic management, security policies, and observability. Demonstrates zero-trust networking, mutual TLS, and advanced traffic routing.

[View Project →](./projects/14-service-mesh-implementation/)

---

### Data Engineering & Databases

#### [Project 2: Database Migration Platform](./projects/2-database-migration-platform/)
**Status:** 🔵 Planned · **Tech:** Python, PostgreSQL, MySQL, AWS DMS
Automated database migration framework supporting schema conversion, data replication, and validation. Handles large-scale migrations (100M+ rows) with minimal downtime using AWS DMS and custom Python orchestration.

**Key Features:**
- Zero-downtime migration with CDC (Change Data Capture)
- Automated schema conversion and validation
- Parallel data transfer with progress tracking
- Rollback procedures and point-in-time recovery
- Performance benchmarking pre/post migration

[View Project →](./projects/2-database-migration-platform/)

---

#### [Project 4: Real-time Data Pipeline (Kafka)](./projects/4-realtime-data-pipeline/)
**Status:** 🔵 Planned · **Tech:** Apache Kafka, Kafka Connect, ksqlDB, Flink
Event-driven data pipeline processing 10K+ events/second with Kafka Streams and Flink for real-time analytics. Includes schema registry, dead-letter queues, and exactly-once processing semantics.

[View Project →](./projects/4-realtime-data-pipeline/)

---

#### [Project 13: Multi-Region Database Replication](./projects/13-multi-region-database-replication/)
**Status:** 🔵 Planned · **Tech:** PostgreSQL, AWS Aurora Global Database, Patroni
Active-active database replication across AWS regions with automated failover and conflict resolution. Implements read/write splitting and geo-routing for optimal latency.

[View Project →](./projects/13-multi-region-database-replication/)

---

#### [Project 21: Data Lake & Analytics Platform](./projects/21-data-lake-analytics/)
**Status:** 🔵 Planned · **Tech:** AWS S3, Glue, Athena, Spark, Delta Lake
Scalable data lake architecture with automated ETL pipelines, data quality checks, and self-service analytics. Supports structured, semi-structured, and unstructured data with ACID transactions via Delta Lake.

[View Project →](./projects/21-data-lake-analytics/)

---

#### [Project 24: GraphQL Federation Gateway](./projects/24-graphql-federation/)
**Status:** 🔵 Planned · **Tech:** Apollo Federation, GraphQL, Node.js, TypeScript
Microservices data aggregation layer using GraphQL Federation. Unified API gateway for 10+ backend services with schema stitching, caching, and authentication.

[View Project →](./projects/24-graphql-federation/)

---

### MLOps & AI Platforms

#### [Project 6: MLOps Platform with Experiment Tracking](./projects/6-mlops-platform/)
**Status:** 🔵 Planned · **Tech:** MLflow, Optuna, Kubernetes, Kubeflow
End-to-end ML pipeline with experiment tracking, hyperparameter optimization, and model serving. Includes automated retraining, A/B testing, and model monitoring with drift detection.

**Key Features:**
- MLflow for experiment tracking and model registry
- Optuna for hyperparameter optimization (Bayesian search)
- Automated model deployment to Kubernetes with Seldon Core
- Model performance monitoring with Evidently AI
- Feature store integration with Feast

[View Project →](./projects/6-mlops-platform/)

---

#### [Project 20: Model Serving & Inference API](./projects/20-model-serving-inference/)
**Status:** 🔵 Planned · **Tech:** TensorFlow Serving, TorchServe, FastAPI, Triton
High-throughput ML model serving platform supporting TensorFlow, PyTorch, and ONNX models. Includes batching, GPU optimization, and multi-model serving.

[View Project →](./projects/20-model-serving-inference/)

---

#### [Project 23: Feature Store & ML Data Platform](./projects/23-feature-store-ml-data/)
**Status:** 🔵 Planned · **Tech:** Feast, Tecton, DynamoDB, Redis, Spark
Centralized feature store for ML with low-latency online serving and batch offline processing. Supports feature versioning, point-in-time correct joins, and feature monitoring.

[View Project →](./projects/23-feature-store-ml-data/)

---

### Platform Engineering & Developer Tools

#### [Project 5: Internal Developer Platform (IDP)](./projects/5-internal-developer-platform/)
**Status:** 🔵 Planned · **Tech:** Backstage, Terraform, Kubernetes, ArgoCD
Self-service platform for developers to provision environments, deploy applications, and access documentation. Built on Backstage with automated infrastructure provisioning via Terraform.

**Key Features:**
- Service catalog with dependency tracking
- Self-service environment provisioning
- Integrated CI/CD pipelines
- Cost transparency per service
- Golden path templates for common architectures

[View Project →](./projects/5-internal-developer-platform/)

---

#### [Project 7: Automated Testing Framework](./projects/7-automated-testing-framework/)
**Status:** 🔵 Planned · **Tech:** Pytest, Selenium, Playwright, GitHub Actions
Comprehensive testing framework with unit, integration, and E2E tests. Includes visual regression testing, accessibility testing (axe-core), and performance testing (Lighthouse).

[View Project →](./projects/7-automated-testing-framework/)

---

#### [Project 8: API Gateway & Rate Limiting Platform](./projects/8-api-gateway-rate-limiting/)
**Status:** 🔵 Planned · **Tech:** Kong, Nginx, Redis, Lua scripting
High-performance API gateway with advanced rate limiting, authentication, and traffic management. Handles 50K+ req/sec with Redis-backed distributed rate limiting.

[View Project →](./projects/8-api-gateway-rate-limiting/)

---

#### [Project 9: Secrets Management Vault](./projects/9-secrets-management-vault/)
**Status:** 🔵 Planned · **Tech:** HashiCorp Vault, Kubernetes, OIDC
Enterprise secrets management with dynamic credentials, encryption-as-a-service, and automated rotation. Integrates with Kubernetes, AWS, and database engines.

[View Project →](./projects/9-secrets-management-vault/)

---

#### [Project 12: Disaster Recovery Automation](./projects/12-disaster-recovery-automation/)
**Status:** 🔵 Planned · **Tech:** Terraform, Ansible, AWS Backup, PBS
Automated disaster recovery with infrastructure-as-code rebuild, data restoration orchestration, and regular DR drills. Achieves RTO of 4-8 hours and RPO of 24-48 hours.

[View Project →](./projects/12-disaster-recovery-automation/)

---

#### [Project 19: ChatOps & Incident Management](./projects/19-chatops-incident-management/)
**Status:** 🔵 Planned · **Tech:** Slack, PagerDuty, Python, Bolt Framework
Incident response automation via Slack with automated runbook execution, alert grouping, and post-incident review workflows. Integrates with PagerDuty for on-call management.

[View Project →](./projects/19-chatops-incident-management/)

---

### Blockchain & Web3

#### [Project 10: Blockchain Smart Contract Platform](./projects/10-blockchain-smart-contract-platform/)
**Status:** 🔵 Planned · **Tech:** Solidity, Hardhat, Ethers.js, OpenZeppelin
ERC-20 token contract with staking mechanism, governance voting, and timelock controls. Includes comprehensive testing (Hardhat), gas optimization, and security best practices.

**Key Features:**
- ERC-20 token with burn and mint capabilities
- Staking rewards with compound interest
- Governance with proposal voting and timelock
- Multi-signature wallet for admin operations
- Comprehensive unit and integration tests (95%+ coverage)

[View Project →](./projects/10-blockchain-smart-contract-platform/)

---

### Security & Compliance

#### [Project 15: Zero Trust Network Architecture](./projects/15-zero-trust-network/)
**Status:** 🔵 Planned · **Tech:** Teleport, Boundary, SPIFFE/SPIRE, Istio
Zero-trust networking with identity-based access, just-in-time privileges, and continuous verification. Eliminates VPNs with certificate-based authentication.

[View Project →](./projects/15-zero-trust-network/)

---

#### [Project 16: Security Scanning & Vulnerability Management](./projects/16-security-scanning-vulnerability/)
**Status:** 🔵 Planned · **Tech:** Trivy, Snyk, SonarQube, OWASP Dependency-Check
Automated security scanning pipeline for containers, code, and dependencies. Integrates with CI/CD for shift-left security with policy enforcement.

[View Project →](./projects/16-security-scanning-vulnerability/)

---

#### [Project 17: Compliance Automation (SOC 2 / ISO 27001)](./projects/17-compliance-automation/)
**Status:** 🔵 Planned · **Tech:** Open Policy Agent, Cloud Custodian, Terraform
Automated compliance checking for SOC 2 and ISO 27001 controls. Policy-as-code for infrastructure, continuous compliance monitoring, and automated evidence collection.

[View Project →](./projects/17-compliance-automation/)

---

### Observability & Performance

#### [Project 18: Distributed Tracing Platform](./projects/18-distributed-tracing/)
**Status:** 🔵 Planned · **Tech:** Jaeger, OpenTelemetry, Grafana Tempo
End-to-end distributed tracing for microservices with automatic instrumentation. Correlates traces with logs and metrics for complete observability.

[View Project →](./projects/18-distributed-tracing/)

---

### Advanced & Emerging Technologies

#### [Project 22: IoT Data Ingestion Platform](./projects/22-iot-data-ingestion/)
**Status:** 🔵 Planned · **Tech:** AWS IoT Core, MQTT, TimescaleDB, Grafana
IoT telemetry pipeline handling 10K+ devices with MQTT protocol, time-series data storage, and real-time alerting. Supports OTA firmware updates and device management.

[View Project →](./projects/22-iot-data-ingestion/)

---

#### [Project 25: Edge AI Inference (ONNX Runtime)](./projects/25-edge-ai-inference/)
**Status:** 🔵 Planned · **Tech:** ONNX Runtime, TensorRT, C++, Python
Optimized ML model inference at the edge with quantization, pruning, and hardware acceleration (GPU/FPGA). Reduces model size by 75% while maintaining accuracy.

[View Project →](./projects/25-edge-ai-inference/)

---

## 📖 Documentation & Knowledge Base

### [Enterprise Wiki Documentation System](./wiki/)
Comprehensive Wiki.js documentation covering all portfolio projects with operational runbooks, playbooks, and handbooks.

**What's Included:**
- **30+ Runbooks**: Incident response procedures for common alerts and issues
  - Infrastructure runbooks: Host Down, Disk Space Low, High CPU, Memory Exhaustion
  - Database runbooks: Backup Failure, Connection Issues, Slow Queries, Replication Lag
  - Security runbooks: IPS Alerts, Unauthorized Access, Malware Detection
  - Monitoring runbooks: Prometheus Scrape Failures, Alert Storm, Log Ingestion Issues
- **15+ Playbooks**: End-to-end process workflows for complex scenarios
  - Disaster Recovery Playbook (RTO: 4-8hrs, RPO: 24-48hrs)
  - Backup & Recovery, Incident Response, Deployment, Change Management
  - Security Hardening, Penetration Testing, Patch Management
  - Performance Tuning, Capacity Planning
- **5+ Handbooks**: Comprehensive reference guides and standards
  - Engineer's Handbook: Terraform standards, security best practices, quality gates
  - Operations Handbook: Day-to-day operational procedures
  - Security Handbook: Security policies and compliance requirements
  - Monitoring Handbook: Observability best practices and golden signals
- **Project Documentation**: Complete implementation guides for all portfolio projects

**Quick Start:**
- [Wiki Home](./wiki/home.md) - Main landing page with full navigation
- [Getting Started Guide](./wiki/getting-started.md) - How to use the wiki
- [Runbooks Index](./wiki/runbooks/index.md) - All incident response procedures
- [Playbooks Index](./wiki/playbooks/index.md) - All process workflows

**Setup Your Own Wiki:**
- [📘 Wiki.js Setup Guide](./docs/wiki-js-setup-guide.md) - Complete deployment guide
  - Docker Compose deployment (recommended)
  - Node.js + PM2 deployment
  - Kubernetes deployment with Helm
  - PostgreSQL setup and configuration
  - Backup and disaster recovery procedures

---

### [Interactive Learning Paths Application](./enterprise-wiki-app/)
React-based interactive learning path tracker for portfolio skills development across SDE, DevOps, QA, and Architecture roles.

**Features:**
- Role-specific learning paths (SDE, DevOps, QA, Solutions Architect)
- 52-week curriculum with weekly milestones
- Progress tracking with completion status
- Certificate recommendations (AWS, Azure, Kubernetes, Security)
- Project integration with portfolio projects
- Interactive timeline visualization

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Vite, Lucide React icons

[View Application →](./enterprise-wiki-app/)

---

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