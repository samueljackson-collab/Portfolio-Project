# Comprehensive Portfolio Code Generation Prompts

This playbook contains ready-to-use prompts for AI code generators (Claude, ChatGPT, Gemini, etc.) to produce production-quality code and documentation across the entire portfolio. It prioritizes documenting existing homelab work first, then delivers quick-win cloud projects, and finally ensures evidence collection and quality hardening.

## Phase Plan

- **Phase 1 (Weeks 1-2):** Document existing homelab implementations, starting with the monitoring stack (PRJ-HOME-002), followed by network infrastructure (PRJ-HOME-001) and virtualization services.
- **Phase 2 (Weeks 3-6):** Build minimal viable cloud projects, expanding the existing RDS Terraform module into a full AWS infrastructure project and delivering 5-6 quick wins.
- **Phase 3 (Weeks 7-8):** Capture operational evidence (screenshots and artifacts) for the monitoring stack and other delivered services.
- **Phase 4 (Weeks 9-10):** Apply quality improvements, code hardening, and best practices across all generated assets.

## How to Use These Prompts

1. Copy the selected prompt verbatim into your AI code generator.
2. Supply any missing inputs (environment specifics, secrets, URLs) before execution.
3. Run one prompt at a time and review outputs immediately while context is fresh.
4. Test, iterate if needed, and commit only after validation.
5. Store generated code in the directory structures specified within each prompt.

---

## Backbone → Breadth → Polish: Portfolio Delivery Plan

**Phase 0 — Standards (do once, reuse everywhere)**

- **Repo scaffolding:** `/projects/PXX-*`, `docs/`, `runbooks/`, `scripts/`, `.github/workflows/`, `helm/`, `infra/`, `tests/`.
- **Universal Definition of Done (DoD):**
  - Code runs locally and in cloud (or simulated env) with a single command.
  - README (exec summary, arch, setup, run, test, ops, KPIs), PNG diagram, ADR.
  - Tests: unit + an end-to-end or integration check; CI must run them.
  - Observability: basic metrics/logs + one alert rule; trace or dashboard link if applicable.
  - Evidence: screenshot(s)/CLI logs + short “demo script.”
- **Project boilerplate generator:** a single script that drops identical structure, linting, test harness, and CI skeleton into any `/projects/PXX-*` directory.

**Phase 1 — Backbone (unlock everything else)**

- Ship slim but working “walking skeletons” for **P01 (IaC), P03 (CI/CD GitOps), P25 (Observability)**.
- Wire common services once: container registry, secret management, Prometheus + Grafana + Jaeger (or Loki), artifact storage.
- Add a shared Release Checklist (build, scan, deploy, verify, roll back).

**Phase 2 — First verticals (ship complete demos)**

- Data & AI: **P09 (RAG), P10 (Data Lake), P07 (MLOps)**.
- Reliability & DR: **P21 (DR), P02 (DB migration)**.
- App platform: **P05 (mesh)** or start with single-cloud P03 baseline extended to canary.

**Phase 3 — Remainder in pods**

- Security pod: **P04, P11, P14, P15**.
- Emerging tech pod: **P16–P20**.
- Compute pod: **P06, P08, P22–P24**.

**Phase 4 — Polish & recruiter demo**

- Demo-day script: run 2–3 projects side-by-side (e.g., P09 + P25; or P03 + P01 + P21).
- Evidence pack: GIFs/mp4s, dashboards JSON, “one-pager” for each project.

### Cross-Cutting Checklists (apply to every project)

- **Code & Config:** containerized or reproducible env; `.env.example`; IaC or script for cloud resources; `Makefile` or `scripts/{up,down,deploy,destroy}.sh`.
- **Security:** secrets via env/manager; no secrets in git; SAST/DAST/container scan in CI; license & SBOM artifact.
- **Docs & Visuals:** README, ADR, architecture PNG, demo steps, evidence folder; “Ops quicksheet” covering start/stop, logs, rollback.
- **Tests & CI:** unit + 1 integration/E2E; CI: lint → test → build → scan → package → (deploy if tagged); status badge + test coverage artifact.
- **Observability:** expose metrics/logs; one alert (error rate/latency/disk/etc.); link to dashboard or sample trace.

### Work Plan by Week (compress/expand as needed)

- **Week 1 (backbone):** P01 dev VPC deployed; P03 pipeline running on sample app; P25 stack up locally; universal boilerplate + DoD locked.
- **Week 2 (first verticals):** P09 minimal RAG; P10 ingest + one query; P02 synthetic migration dry-run.
- **Week 3 (security & collab):** P04 security CI; P14 SIEM ingest + 1 detection; P22 collaborative doc demo.
- **Week 4 (mesh/DR/edge):** P21 DR drill; P05 single-cloud → multi-cluster plan; P18 edge inference proof; polish evidence & demos.

### “Done” Audit Sheet (reuse for each project)

- Runs locally via `make up` or `docker compose up`.
- Cloud deploy (or lab) via single script.
- README + ADR + diagram PNG committed.
- Unit test(s) + one integration/E2E in CI green.
- Metrics exposed; 1 alert + 1 dashboard/trace.
- Evidence folder with screenshots/logs & a 60-sec demo script.
- Release notes and rollback steps.

---

### Shared Release Checklist (reuse verbatim)

1. Build → Test → Scan (SAST/DAST/SCA/SBOM) → Package.
2. Deploy to target environment with parameterized config.
3. Verify health (smoke + integration) and observability signals (metrics/logs/traces, alerts wired).
4. Capture evidence (screenshots/logs, demo script) and publish artifacts.
5. If verification fails: initiate rollback script, file incident note, and open fix ticket.

---

## Copy-Paste Prompt Pack for Projects P01–P25

Use these prompts directly in your code-generation agent. Replace **PXX** with the project id and adjust names/regions as needed. Each prompt returns code, docs (README + ADR), tests, diagrams (Mermaid/PlantUML → PNG), Makefile/scripts, and a runnable local demo.

### P01 — AWS Infrastructure Automation (3-tier VPC, ALB, ASG, RDS)
```
Create projects/P01-aws-infra with Terraform modules for VPC (3 AZs; public/private/db), IGW, 3× NAT, route tables, SGs (least-priv), IAM baseline, EC2 ASG (user-data), ALB (TLS), RDS Postgres (Multi-AZ + optional read-replica). Include: infra/ modules, environments/{dev,stage,prod} with tfvars, scripts/{validate,plan,apply,destroy}.sh, outputs, tags, diagrams (Mermaid → PNG), README (cost + risks), ADR, unit tests with terratest or tflint. Provide sample variables.tf defaults and a dev plan/apply transcript.
```

### P02 — Zero-Downtime DB Migration (MySQL→Postgres with DMS)
```
Create projects/P02-db-migration with IaC for AWS DMS, schema conversion, dual-write proxy (tiny Node/Python), consistency checker (checksums, row counts, drift), cutover and rollback scripts, synthetic dataset + load gen, runbook PDF, and KPI report template. Include tests/integration to seed, migrate, validate, and assert zero downtime in docker-compose.
```

### P03 — K8s CI/CD (GitHub Actions + ArgoCD + Canary)
```
Create projects/P03-k8s-cicd with sample service (REST), Dockerfile, Helm chart, ArgoCD app, Istio VS for 10%→100% canary, GH Actions pipeline (lint, unit, SCA, SAST, build, SBOM, push, helm upgrade, smoke, rollback on health). README with pipeline diagram and make kind-up deploy canary roll-back targets.
```

### P04 — DevSecOps Pipeline (Security gates)
```
Create projects/P04-devsecops adding SAST (bandit/semgrep), DAST (ZAP), deps scan (safety/snyk), container scan (trivy), secrets scan (gitleaks), pre-commit hooks, SARIF uploads, and a minimal vulnerable app to produce findings. Include policy thresholds, sample reports, and a ‘fix PR’ generator script.
```

### P05 — Multi-Cloud Service Mesh (Istio across EKS/AKS/GKE)
```
Create projects/P05-multicloud-mesh: Terraform for EKS, AKS, GKE; Istio multi-cluster install (east-west GW, trust domain, endpoint discovery), sample services, cross-cluster failover demo, mesh-link.sh, diagrams, and soak test that kills pods in one cloud and verifies failover.
```

### P06 — Real-time Streaming (Kafka + Flink)
```
Create projects/P06-streaming: docker-compose (Kafka, schema registry), Python producers, Flink job (tumbling windows, exactly-once sink to Postgres/Parquet), late-event handling, load gen, dashboards, and E2E tests asserting counts & windows.
```

### P07 — MLOps Pipeline (Kubeflow + MLflow)
```
Create projects/P07-mlops: Kubeflow pipeline (extract→prep→train→eval→promote), MLflow tracking & model registry, drift monitor, canary model rollout to FastAPI. Include synthetic dataset, unit tests for feature code, reproducible seeds, and a metrics dashboard JSON.
```

### P08 — Serverless ETL (Lambda)
```
Create projects/P08-serverless-etl: Lambda (Python) triggered by S3 put or Kinesis; transform JSON→Dynamo/Parquet; IaC (SAM/Terraform), retries/DLQ, alarms; local tests with mocked events; README with cost model and perf targets.
```

### P09 — Advanced AI Chatbot (RAG)
```
Create projects/P09-rag-chatbot: FastAPI + LangChain; document ingestor; embeddings + FAISS; query → retrieve → answer with citations; streaming responses; eval harness (exact-match & semantic); Docker; tests; prompt/guardrail docs; minimal UI; evidence screenshots.
```

### P10 — Data Lake & Analytics (Iceberg/Delta)
```
Create projects/P10-datalake: Spark job to ingest CSV→Parquet; register Iceberg tables; schema evolution demo; partitioning; Athena/Trino queries; Glue catalog; retention policies; README with query examples and perf notes; tests verifying counts and schema.
```

### P11 — Zero-Trust (SPIFFE/Envoy mTLS)
```
Create projects/P11-zero-trust: SPIRE server/agents, workload SVIDs, Envoy sidecars enforcing mTLS + authz; demo app with a denied and a permitted call; policies as code; diagrams; test script showing 403 vs 200 paths.
```

### P12 — Smart Contracts (Hardhat)
```
Create projects/P12-smart-contracts: Hardhat scaffold; Solidity ERC-20 or crowdfunding contract; unit tests; coverage; deploy to testnet; minimal web client; threat model; gas report; README with steps and screenshots.
```

### P13 — Quantum-Safe Crypto (Kyber KEM demo)
```
Create projects/P13-quantum-safe: Python demo using Kyber (liboqs or wrapper); keygen/encap/decap; encrypt sample secret; perf timings; hybrid TLS discussion; CLI interface; README with trade-offs; tests verifying correctness.
```

### P14 — Advanced Cybersecurity (SIEM/SOAR)
```
Create projects/P14-siem-soar: ELK or Loki+Grafana stack; log ingestors; detection rules (failed logins, beaconing); SOAR script (Python) to disable user/quarantine pod; synthetic attack dataset; dashboards JSON; runbook and screenshots.
```

### P15 — IAM / SSO (Keycloak, OIDC/SAML)
```
Create projects/P15-iam-sso: Keycloak docker; realm + client config; sample app with OIDC login; roles/claims → RBAC; infra examples for cloud IAM policies; login flow diagram; test script for token validation and role enforcement.
```

### P16 — IoT Data Platform (MQTT + Timescale)
```
Create projects/P16-iot-platform: Mosquitto broker; Python device simulators; subscriber writing to Timescale; schema & retention; dashboards; offline buffer/reconnect logic; tests verifying ingestion pipeline.
```

### P17 — Quantum Computing (Qiskit)
```
Create projects/P17-quantum: notebook(s) showing Bell state + small Grover; circuit diagrams; measurement histograms; markdown explaining gates; requirements.txt; results images.
```

### P18 — Edge AI Inference (TFLite/ONNX)
```
Create projects/P18-edge-ai: convert MobileNet to TFLite; inference script; quantization variants; FPS/latency logs; device notes; tests comparing outputs across variants.
```

### P19 — AR/VR (WebXR + Three.js)
```
Create projects/P19-ar-vr: minimal WebXR site; interactive 3D object; tap-to-rotate; feature detection; deployable static site; screenshots and a short demo GIF; README with device caveats.
```

### P20 — 5G Network Slicing (Open5GS lab)
```
Create projects/P20-5g-slicing: dockerized Open5GS lab; two slices (eMBB vs URLLC), config diffs; traffic generator; measurements (throughput/latency); lab guide and diagrams.
```

### P21 — Multi-Region DR (Failover)
```
Create projects/P21-dr: Terraform for two regions; Route53 health checks + DNS failover; cross-region DB replication; DR drill script; RTO/RPO report template; evidence logs/screenshots.
```

### P22 — Real-time Collaboration (CRDT)
```
Create projects/P22-collab: Node WebSocket server + Yjs client; shared doc demo; offline reconciliation; load test; latency budget; README with sequence diagram; tests for conflict resolution.
```

### P23 — GPU Compute (CUDA)
```
Create projects/P23-gpu-compute: C++ CPU vs CUDA matrix-multiply; NVCC build; timing harness; correctness check; chart of speedup; README with tuning notes.
```

### P24 — Autonomous DevOps (AIOps)
```
Create projects/P24-autonomous-devops: agent polling Prometheus; predicts load; scales k8s deployments; safety rails + manual override; training loop on historical metrics; pseudo-code + working MVP; tests with synthetic spikes.
```

### P25 — Observability (Prometheus/Grafana/OpenTelemetry)
```
Create projects/P25-observability: Prometheus scraping two services; OpenTelemetry SDK in demo service exporting to Jaeger; Grafana dashboard JSON; alert rules (error rate/latency); README with screenshots; tests that hit endpoints and assert metrics.
```

---

---

## Prompt 1: Complete Monitoring Stack Implementation (PRJ-HOME-002)
```
CONTEXT: Build a production-ready monitoring stack for my DevOps portfolio. This must be enterprise-grade with comprehensive documentation, security best practices, and operational excellence.

TECH STACK: Prometheus, Grafana, Loki, Alertmanager, Node Exporter, cAdvisor, Docker Compose

REQUIRED OUTPUT STRUCTURE:
projects/01-sde-devops/PRJ-SDE-002/
├── docker-compose.yml (orchestrates all services)
├── prometheus/
│   ├── prometheus.yml (complete configuration)
│   ├── alerts/rules.yml (production alert rules)
│   └── recording-rules.yml (performance optimization)
├── grafana/
│   ├── provisioning/datasources/datasources.yml
│   ├── provisioning/dashboards/dashboards.yml
│   └── dashboards/ (4 complete JSON dashboards)
├── alertmanager/
│   └── alertmanager.yml (routing & notifications)
├── loki/
│   └── loki-config.yml (log aggregation)
├── promtail/
│   └── promtail-config.yml (log shipping)
├── scripts/
│   ├── deploy.sh (automated deployment)
│   ├── health-check.sh (validation)
│   └── backup.sh (disaster recovery)
├── docs/
│   ├── OPERATIONS.md (runbook)
│   ├── TROUBLESHOOTING.md (diagnostic guide)
│   └── SECURITY.md (hardening guide)
└── README.md (comprehensive documentation)

TECHNICAL REQUIREMENTS:
1. Docker Compose: 7 services with health checks, resource limits, restart policies; dual networks (frontend/backend); named volumes; .env support; bind to 127.0.0.1; no default passwords.
2. Prometheus: scrape jobs for prometheus, node-exporter, cadvisor, grafana, loki, proxmox; 15s scrape interval; 15-day retention; Alertmanager integration; service discovery.
3. Alert Rules: critical/warning/info rules for availability, CPU/memory, disk space, exporter status, container restarts.
4. Grafana Dashboards: infrastructure overview, host details, container monitoring, logs explorer.
5. Production Features: health checks, resource limits, non-root users, backups, troubleshooting guides.

CODE QUALITY: Senior-level comments (explain WHY), comprehensive error handling, no hardcoded secrets, production-ready configuration.

GENERATE: Complete, working code deployable via `docker-compose up -d`.
```

## Prompt 1a: Automation Agents for Build, Test, Deploy, Documentation, Scanning, and Push
```
CONTEXT: Use the following agent definitions to orchestrate CI/CD and documentation workflows for any project generated from this playbook. Each agent is responsible for a distinct phase and should be invoked with the specified inputs and outputs.

AGENT DEFINITIONS:
[
  {
    "name": "BuildAgent",
    "task": "build",
    "description": "Compile or build the project artifacts from source code.",
    "inputs": ["source_code", "build_config"],
    "outputs": ["build_artifacts", "build_logs"],
    "steps": [
      "Fetch or receive source code and configuration",
      "Execute build commands (e.g., compile, npm/yarn install for Node, mvn for Java, etc.)",
      "Produce build artifacts (binaries, containers, static files)",
      "Return build status and logs"
    ]
  },
  {
    "name": "TestAgent",
    "task": "test",
    "description": "Run automated tests (unit, integration, etc.) to validate the build.",
    "inputs": ["build_artifacts", "test_suite"],
    "outputs": ["test_report", "coverage_metrics"],
    "steps": [
      "Execute test suite against the build artifacts or code",
      "Collect results (passed/failed tests) and code coverage",
      "Generate a test report (e.g., JUnit XML, coverage report)",
      "Return test outcomes and key metrics"
    ]
  },
  {
    "name": "DeployAgent",
    "task": "deploy",
    "description": "Deploy the build artifacts to a target environment (dev/stage/prod).",
    "inputs": ["build_artifacts", "deployment_config"],
    "outputs": ["deployment_logs", "environment_status"],
    "steps": [
      "Determine target environment and deployment parameters",
      "Provision or update infrastructure (IaC or cloud APIs if needed)",
      "Deploy artifacts (e.g., push container to registry, apply K8s manifests)",
      "Verify deployment health (ping health endpoints, etc.)",
      "Return deployment status and logs"
    ]
  },
  {
    "name": "DocAgent",
    "task": "document",
    "description": "Generate or update documentation based on code and config changes.",
    "inputs": ["source_code", "architecture_docs", "changelog"],
    "outputs": ["documentation_pages", "doc_site_updates"],
    "steps": [
      "Extract comments, docstrings, and commit messages as needed",
      "Update Markdown/HTML documentation pages for the project",
      "Generate diagrams or visualizations if configured (Mermaid, etc.)",
      "Publish documentation to the docs site or wiki",
      "Return confirmation of updated docs (pages list or diff)"
    ]
  },
  {
    "name": "ScanAgent",
    "task": "scan",
    "description": "Perform security and quality scans (SAST, DAST, dependency checks).",
    "inputs": ["source_code", "build_artifacts"],
    "outputs": ["scan_reports", "alerts"],
    "steps": [
      "Run static code analysis tools (linters, SAST scanners) on source",
      "Scan build artifacts (containers, packages) for vulnerabilities (dependency scan, SCA)",
      "Perform dynamic analysis if applicable (running app scans)",
      "Collect and format findings into reports (e.g., SARIF, HTML)",
      "Return scan results and highlight any critical issues"
    ]
  },
  {
    "name": "PushAgent",
    "task": "push",
    "description": "Push code or artifacts to remote repositories or registries.",
    "inputs": ["build_artifacts", "version_tag"],
    "outputs": ["repository_status", "artifact_url"],
    "steps": [
      "Tag the build artifacts with version or commit ID",
      "Push container images to Docker/GitHub Container Registry (if applicable)",
      "Upload binaries/packages to package registries or artifact storage",
      "Push committed code changes to source repository (if not already)",
      "Return URLs or references to pushed artifacts"
    ]
  }
]

USAGE: Copy this agent block into your orchestration tool (e.g., LangChain, CrewAI) and invoke agents in sequence: BuildAgent → TestAgent → ScanAgent → DeployAgent → DocAgent → PushAgent. Provide environment-specific configs (credentials, endpoints, flags) at runtime and fail-fast on any unsuccessful agent output before proceeding to the next stage.
```

## Prompt 2: AWS Infrastructure Automation (Terraform)
```
CONTEXT: Expand my basic RDS Terraform module into a complete multi-tier AWS infrastructure project demonstrating cloud engineering expertise.

REQUIRED OUTPUT STRUCTURE:
projects/01-aws-infrastructure-automation/
├── modules/
│   ├── vpc/ (complete VPC with NAT, IGW, subnets)
│   ├── rds/ (PostgreSQL with Multi-AZ, encryption)
│   ├── compute/ (ALB + Auto Scaling Group)
│   ├── cdn/ (CloudFront + S3)
│   └── security/ (IAM roles, security groups)
├── examples/
│   └── complete/ (working deployment example)
├── tests/
│   └── terraform_test.go (Terratest validation)
├── docs/
│   ├── ARCHITECTURE.md (diagrams & explanation)
│   ├── DEPLOYMENT.md (step-by-step guide)
│   └── COST_ESTIMATION.md (pricing breakdown)
└── main.tf (root module)

TECHNICAL SPECIFICATIONS:
1. VPC: two AZs, public/private subnets, NAT per AZ, IGW, route tables, VPC endpoints (S3, SSM).
2. RDS: PostgreSQL 13+, Multi-AZ, KMS encryption, automated backups, enhanced monitoring, tuned parameter group, minimal-access SG.
3. Compute: internet-facing ALB, ASG (2-4 instances), launch template with user data, target groups with health checks, least-privilege SGs.
4. Security: IAM roles with minimum permissions, SGs with descriptive rules, KMS key, CloudTrail logging.
5. Production: Terraform 1.0+, variable validation, outputs, S3 backend state locking, workspace support.

GENERATE: Production-ready Terraform code aligning with AWS Well-Architected principles.
```

## Prompt 3: Kubernetes GitOps Pipeline
```
CONTEXT: Create a complete GitOps pipeline for Kubernetes using ArgoCD or Flux, demonstrating modern cloud-native deployment practices.

REQUIRED OUTPUT STRUCTURE:
projects/03-kubernetes-gitops-pipeline/
├── infrastructure/
│   ├── terraform/ (EKS cluster provisioning)
│   └── helm/ (ArgoCD installation)
├── applications/
│   ├── base/ (common manifests)
│   ├── overlays/
│   │   ├── development/
│   │   ├── staging/
│   │   └── production/
│   └── helm-charts/ (custom charts)
├── gitops-config/
│   ├── argocd-applications/ (App of Apps pattern)
│   └── kustomization.yaml
├── pipeline/
│   ├── .github/workflows/ (CI/CD workflows)
│   ├── scripts/ (validation & deployment)
│   └── tests/ (Kubernetes validation)
└── docs/
    ├── GITOPS_PRINCIPLES.md
    ├── DEPLOYMENT_GUIDE.md
    └── TROUBLESHOOTING.md

TECHNICAL SPECIFICATIONS:
- Terraform EKS provisioning with node groups, network policies, storage classes.
- ArgoCD installed via Helm; Application of Applications pattern; Kustomize overlays; Helm charts for complex apps.
- Sample apps: 3-tier web app, monitoring stack, logging stack, certificate management.
- CI/CD: GitHub Actions for build/test, image scanning, manifest validation, automated promotion.
- Security: pod security standards, network policies, resource limits, external-secrets, RBAC.

GENERATE: GitOps implementation that auto-deploys across dev/staging/prod with full automation and security controls.
```

## Prompt 4: Network Infrastructure Documentation (PRJ-HOME-001)
```
CONTEXT: Create comprehensive network documentation for my homelab infrastructure, suitable for enterprise portfolio demonstration.

REQUIRED OUTPUT STRUCTURE:
projects/06-homelab/PRJ-HOME-001/
├── diagrams/
│   ├── physical-topology.drawio
│   ├── logical-architecture.drawio
│   └── security-zones.drawio
├── configs/
│   ├── unifi-backup/ (actual configuration export)
│   ├── firewall-rules.csv
│   └── vlan-configuration.json
├── docs/
│   ├── NETWORK-ARCHITECTURE.md
│   ├── VLAN-DESIGN.md
│   ├── SECURITY-POLICY.md
│   ├── SWITCH-PORT-MAP.md
│   └── TROUBLESHOOTING.md
└── scripts/
    ├── network-scan.sh
    └── config-backup.sh

TECHNICAL CONTENT REQUIREMENTS:
- Physical topology and logical VLAN architecture with CIDR ranges.
- VLANs: 1 (Management 192.168.1.0/24), 10 (Trusted 192.168.10.0/24), 20 (IoT 192.168.20.0/24), 30 (Guest 192.168.30.0/24), 40 (Servers 192.168.40.0/24).
- Security policies: inter-VLAN firewall rules, WiFi security, device isolation, threat management.
- Operational documentation: switch port mapping, AP placement, cable management, backup procedures.
- Diagram descriptions for physical topology, security zones, data flow, wireless coverage.

GENERATE: Enterprise-grade network documentation sufficient to rebuild the environment from scratch.
```

## Prompt 5: Complete CI/CD Pipeline with Security Scanning
```
CONTEXT: Build a complete DevSecOps pipeline with automated security scanning, testing, and deployment for a sample application.

REQUIRED OUTPUT STRUCTURE:
projects/04-devsecops-pipeline/
├── application/
│   ├── src/ (sample Python/Node.js app)
│   ├── Dockerfile (multi-stage build)
│   ├── docker-compose.yml (local development)
│   └── tests/ (unit & integration tests)
├── pipeline/
│   ├── .github/workflows/
│   │   ├── ci.yml
│   │   ├── security-scan.yml
│   │   └── cd.yml
│   ├── scripts/
│   │   ├── security-scan.sh
│   │   ├── deploy.sh
│   │   └── smoke-tests.sh
│   └── configs/
│       ├── trivy-config.yaml
│       ├── hadolint-config.yaml
│       └── sonarqube-config.properties
├── infrastructure/
│   ├── kubernetes/
│   ├── terraform/
│   └── monitoring/
└── docs/
    ├── PIPELINE_ARCHITECTURE.md
    ├── SECURITY_SCANNING.md
    └── INCIDENT_RESPONSE.md

TECHNICAL SPECIFICATIONS:
- Sample FastAPI or Express app with health checks and metrics; Docker multi-stage build.
- CI: linters, unit/integration tests, coverage, container build/push.
- Security: SAST (SonarQube/Semgrep), SCA and container scanning (Trivy), secrets detection (Gitleaks), DAST (OWASP ZAP).
- CD: environment promotion, blue-green deploy, automated rollback, smoke tests.
- Observability: pipeline metrics/dashboards, findings aggregation, alerts, compliance reporting.

GENERATE: DevSecOps pipeline demonstrating security-first CI/CD with working code and docs.
```

## Prompt 6: Serverless Data Processing Platform
```
CONTEXT: Create a serverless data processing platform using AWS Lambda, Step Functions, and event-driven architecture.

REQUIRED OUTPUT STRUCTURE:
projects/07-serverless-data-processing/
├── infrastructure/
│   ├── terraform/
│   ├── sam/
│   └── cloudformation/
├── functions/
│   ├── data-ingestion/
│   ├── data-processing/
│   ├── data-validation/
│   └── error-handling/
├── step-functions/
│   ├── data-pipeline.asl.json
│   └── error-workflow.asl.json
├── event-bridges/
│   └── event-rules/
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_FLOW.md
    └── COST_OPTIMIZATION.md

TECHNICAL SPECIFICATIONS:
- Pipeline: S3 trigger, Step Functions orchestration, multiple Lambdas, retries and error handling.
- Lambda (Python): validation/sanitization, transformation/enrichment, DynamoDB operations, CSV/JSON/Parquet handling.
- Infrastructure: S3 with lifecycle policies, DynamoDB with proper indexes, SQS for decoupling, CloudWatch monitoring.
- Observability: structured logging, custom metrics, X-Ray tracing, dashboards and alerts.
- Production: environment-specific config, Secrets Manager, VPC access, cold-start optimizations.

GENERATE: Serverless app that processes S3 uploads, transforms data, and stores results in DynamoDB with robust observability.
```

## Prompt 7: Multi-Cloud Kubernetes Service Mesh
```
CONTEXT: Implement a service mesh across multiple cloud providers using Istio, demonstrating advanced cloud-native networking patterns.

REQUIRED OUTPUT STRUCTURE:
projects/16-multi-cloud-service-mesh/
├── clusters/
│   ├── aws-eks/
│   ├── gcp-gke/
│   └── azure-aks/
├── istio-config/
│   ├── base/
│   ├── gateways/
│   ├── virtual-services/
│   └── security/
├── sample-apps/
│   ├── frontend/
│   ├── backend/
│   └── database/
├── monitoring/
│   └── kiali-dashboards/
└── docs/
    ├── MULTI_CLUSTER_SETUP.md
    ├── SERVICE_MESH_PATTERNS.md
    └── SECURITY_CONSIDERATIONS.md

TECHNICAL SPECIFICATIONS:
- Multi-cluster setup with east-west gateways, CA integration, endpoint discovery.
- Service mesh features: mTLS, traffic splitting/canary, fault injection, circuit breakers.
- Observability: Kiali, Jaeger, Prometheus, Grafana.
- Security: authorization and network policies, secret management, security contexts.
- Sample apps spanning clusters with replicated databases, distributed cache, and cross-cloud messaging.

GENERATE: Multi-cluster service mesh showcasing advanced cloud-native patterns across providers.
```

## Prompt 8: Advanced AI Chatbot with RAG
```
CONTEXT: Build a production-ready AI chatbot with Retrieval Augmented Generation (RAG), vector search, and modern AI/ML practices.

REQUIRED OUTPUT STRUCTURE:
projects/08-advanced-ai-chatbot/
├── backend/
│   ├── app/
│   ├── models/
│   ├── vector_db/
│   └── agents/
├── frontend/
│   ├── react-app/
│   ├── components/
│   └── styles/
├── infrastructure/
│   ├── terraform/
│   ├── docker/
│   └── kubernetes/
├── data/
│   ├── ingestion/
│   ├── processing/
│   └── vectorization/
└── docs/
    ├── ARCHITECTURE.md
    ├── RAG_IMPLEMENTATION.md
    └── DEPLOYMENT_GUIDE.md

TECHNICAL SPECIFICATIONS:
- RAG: document ingestion/chunking, embeddings (OpenAI/Cohere), vector DB (Chroma/Weaviate/Pinecone), semantic search.
- AI/ML: LangChain orchestration, GPT-4 or local LLM, embedding models, prompt templates.
- Backend: FastAPI async API, WebSocket chat, rate limiting/auth, monitoring/logging.
- Frontend: React + TypeScript, real-time chat, document upload, responsive UI.
- Production: caching, error handling/fallbacks, A/B testing for prompts, usage analytics.

GENERATE: Full AI chatbot with RAG pipeline, vector search, and modern UX.
```

## Prompt 9: Complete Portfolio Website & Documentation Hub
```
CONTEXT: Create a comprehensive portfolio website that showcases all projects with interactive demos, documentation, and evidence.

REQUIRED OUTPUT STRUCTURE:
projects/25-portfolio-website/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── backend/
│   ├── api/
│   ├── database/
│   └── auth/
├── content/
│   ├── projects/
│   ├── blog/
│   └── assets/
├── infrastructure/
│   ├── terraform/
│   ├── docker/
│   └── ci-cd/
└── docs/
    ├── CONTRIBUTING.md
    ├── STYLE_GUIDE.md
    └── DEPLOYMENT.md

TECHNICAL SPECIFICATIONS:
- Frontend: React + TypeScript, responsive design, dark/light mode, project filtering/search, interactive demos.
- Project pages: architecture diagrams, code snippets, demo links, screenshots/videos, technical docs.
- Backend: Express or FastAPI, project metadata, contact handling, analytics.
- Content: markdown-based, automated indexing, SEO and social sharing.
- Deployment: S3 + CloudFront, CI/CD pipeline, domain + SSL, monitoring/analytics.

GENERATE: Professional portfolio site with interactive showcases and comprehensive documentation hub.
```

## Prompt 10: Infrastructure as Code Library & Templates
```
CONTEXT: Create a reusable IaC library with Terraform modules, CloudFormation templates, and deployment scripts for common infrastructure patterns.

REQUIRED OUTPUT STRUCTURE:
projects/00-iac-library/
├── terraform-modules/
│   ├── networking/
│   ├── compute/
│   ├── database/
│   ├── security/
│   └── monitoring/
├── cloudformation-templates/
│   ├── stacks/
│   ├── custom-resources/
│   └── best-practices/
├── scripts/
│   ├── deployment/
│   ├── validation/
│   └── cleanup/
├── examples/
│   ├── three-tier-webapp/
│   ├── serverless-api/
│   └── data-lake/
└── docs/
    ├── MODULE_REFERENCE.md
    ├── BEST_PRACTICES.md
    └── CONTRIBUTING.md

TECHNICAL SPECIFICATIONS:
- Terraform modules with standardized inputs/outputs, documentation, examples, Terratest coverage.
- CloudFormation templates with parameter validation, conditions/mappings, outputs, nested stacks.
- Deployment scripts: environment configs, state management, rollback, cost estimation.
- Best practices: security hardening, cost optimization, reliability patterns, performance tuning.
- Testing/validation: unit tests, integration tests, security scanning, compliance checks.

GENERATE: IaC library enabling rapid deployment of common patterns across clouds with embedded best practices.
```

## Implementation Strategy Checklist

- Week 1: Land backbone skeletons (P01 dev VPC, P03 pipeline on sample app, P25 local stack) and lock boilerplate/DoD.
- Week 2: Deliver first verticals (P09 minimal RAG, P10 ingest + query, P02 migration dry-run) with evidence capture.
- Week 3: Security & collaboration focus (P04 security CI, P14 SIEM ingest + detection, P22 collaboration demo).
- Week 4: Mesh/DR/edge push (P21 DR drill, P05 single-cloud to multi-cluster plan, P18 edge inference proof) and polish demos.

These prompts are intentionally exhaustive to produce senior-level, production-ready code and documentation without placeholders. Apply environment-specific settings (secrets, domains, credentials) before deployment.
