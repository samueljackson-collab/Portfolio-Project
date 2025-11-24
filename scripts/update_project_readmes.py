import os
from textwrap import dedent

projects = {
    "1-aws-infrastructure-automation": {
        "summary": "Terraform-driven AWS landing zone with opinionated networking, autoscaled compute, and managed data services for three-tier apps.",
        "entry": "ALB + API Gateway",
        "core": "ECS/EKS Services",
        "data": "Aurora/RDS + ElastiCache",
        "queue": "SQS/SNS",
    },
    "2-database-migration": {
        "summary": "Zero-downtime migration factory moving legacy databases to cloud-native managed services with continuous validation.",
        "entry": "Migration Hub + DMS",
        "core": "Data Migration Workers",
        "data": "Target RDS/Cloud SQL",
        "queue": "Event Bus",
    },
    "3-kubernetes-cicd": {
        "summary": "Kubernetes-native CI/CD platform with GitOps, canary rollouts, and policy-as-code enforcement.",
        "entry": "Git Webhooks",
        "core": "Argo Workflows/Rollouts",
        "data": "Artifact Registry + Helm Repo",
        "queue": "Events/Notifications",
    },
    "4-devsecops": {
        "summary": "DevSecOps reference pipeline integrating SAST/DAST, SBOM, and supply chain controls into release workflows.",
        "entry": "Source Control",
        "core": "Security Scanners",
        "data": "Vulnerability DB",
        "queue": "Policy Engine",
    },
    "5-real-time-data-streaming": {
        "summary": "Streaming data mesh with Kafka, Flink, and OLAP targets for low-latency analytics and event-driven services.",
        "entry": "Producers/API",
        "core": "Kafka + Flink Jobs",
        "data": "Lakehouse/ClickHouse",
        "queue": "Schema Registry",
    },
    "6-mlops-platform": {
        "summary": "End-to-end MLOps platform covering feature store, training pipelines, model registry, and automated deployments.",
        "entry": "Feature/API Gateway",
        "core": "Pipeline Orchestrator",
        "data": "Feature Store + Model Registry",
        "queue": "Event Queue",
    },
    "7-serverless-data-processing": {
        "summary": "Serverless ETL with event-driven ingestion, transformation, and delivery into analytics stores.",
        "entry": "API/Event Bridge",
        "core": "Lambda/Functions",
        "data": "Data Lake + Warehouse",
        "queue": "Queues/Streams",
    },
    "8-advanced-ai-chatbot": {
        "summary": "Enterprise conversational AI with retrieval-augmented generation, guardrails, and omni-channel connectors.",
        "entry": "Channels/Web Chat",
        "core": "LLM Orchestrator",
        "data": "Vector DB + Knowledge Base",
        "queue": "Task Queue",
    },
    "9-multi-region-disaster-recovery": {
        "summary": "Multi-region active/active disaster recovery pattern with automated failover, replication, and chaos drills.",
        "entry": "Global DNS/Anycast",
        "core": "Regional Stacks",
        "data": "Replicated Datastores",
        "queue": "Control Plane",
    },
    "10-blockchain-smart-contract-platform": {
        "summary": "Managed smart contract platform with CI/CD for Solidity, node orchestration, and audit-quality tooling.",
        "entry": "dApp/API Gateway",
        "core": "Validator/Execution Nodes",
        "data": "State DB + IPFS",
        "queue": "Mempool/Event Bus",
    },
    "11-iot-data-analytics": {
        "summary": "IoT ingestion and analytics stack handling device telemetry, edge processing, and fleet observability.",
        "entry": "Device Gateway",
        "core": "Stream Processing/Rules",
        "data": "Time-Series DB + Data Lake",
        "queue": "MQTT Broker",
    },
    "12-quantum-computing": {
        "summary": "Quantum-inspired optimization service with hybrid workflows across classical and quantum hardware.",
        "entry": "API Gateway",
        "core": "Hybrid Job Scheduler",
        "data": "Results Store + Cache",
        "queue": "Job Queue",
    },
    "13-advanced-cybersecurity": {
        "summary": "Cyber defense platform blending SIEM, SOAR, and threat intel automation for rapid response.",
        "entry": "Sensor/Collector",
        "core": "Detection + SOAR",
        "data": "Security Data Lake",
        "queue": "Alert Queue",
    },
    "14-edge-ai-inference": {
        "summary": "Edge AI inference fabric with model distribution, OTA updates, and telemetry feedback loops.",
        "entry": "Edge Gateway",
        "core": "Edge Inference Runtime",
        "data": "Model Repository + Cache",
        "queue": "Control Plane",
    },
    "15-real-time-collaboration": {
        "summary": "Real-time collaboration platform with CRDT-based sync, presence, and media signaling.",
        "entry": "WebSockets/API",
        "core": "Collaboration Engine",
        "data": "State Store + Media Cache",
        "queue": "Signaling Bus",
    },
    "16-advanced-data-lake": {
        "summary": "Governed data lake with medallion architecture, ACID tables, and unified catalog/search.",
        "entry": "Ingestion APIs/Streams",
        "core": "Lakehouse Processing",
        "data": "Bronze/Silver/Gold Tables",
        "queue": "Metadata/Event Bus",
    },
    "17-multi-cloud-service-mesh": {
        "summary": "Multi-cloud service mesh with zero-trust policies, traffic shaping, and cross-cloud observability.",
        "entry": "Ingress Gateway",
        "core": "Service Mesh Control Plane",
        "data": "Config/Policy Store",
        "queue": "Telemetry Bus",
    },
    "18-gpu-accelerated-computing": {
        "summary": "GPU-accelerated compute fabric for AI/HPC workloads with autoscaling and cost-aware scheduling.",
        "entry": "Job API",
        "core": "GPU Scheduler + Operators",
        "data": "Artifact/Model Store",
        "queue": "Work Queue",
    },
    "19-advanced-kubernetes-operators": {
        "summary": "Operator catalog enabling lifecycle automation for stateful and stateless workloads with policy guardrails.",
        "entry": "Kubectl/API",
        "core": "Custom Controllers",
        "data": "CRDs/State Stores",
        "queue": "Event Queue",
    },
    "20-blockchain-oracle-service": {
        "summary": "Blockchain oracle delivering signed real-world data with redundancy, monitoring, and slashing prevention.",
        "entry": "Data Providers",
        "core": "Oracle Nodes",
        "data": "Price/Fact Store",
        "queue": "Signing Queue",
    },
    "21-quantum-safe-cryptography": {
        "summary": "Quantum-safe crypto toolkit adding PQC algorithms, key rotation, and backward-compatible integrations.",
        "entry": "SDK/API",
        "core": "Crypto Services",
        "data": "Key Vault/KMS",
        "queue": "Audit/Event Bus",
    },
    "22-autonomous-devops-platform": {
        "summary": "Self-healing DevOps platform with policy-driven automation, AIOps insights, and closed-loop remediation.",
        "entry": "Developer Portal",
        "core": "Automation Orchestrator",
        "data": "Config/CMDB + Metrics Store",
        "queue": "Workflow Queue",
    },
    "23-advanced-monitoring": {
        "summary": "Holistic monitoring stack with log/metric/trace correlation, SLO management, and synthetic testing.",
        "entry": "Telemetry Collectors",
        "core": "Metrics/Logs/Trace Pipeline",
        "data": "TSDB + Trace Store",
        "queue": "Alert Router",
    },
    "24-report-generator": {
        "summary": "Report automation service that stitches datasets into governed, distribution-ready narratives and PDFs.",
        "entry": "Report API/UI",
        "core": "Template Engine + Scheduler",
        "data": "Data Warehouse + Object Storage",
        "queue": "Job Queue",
    },
    "25-portfolio-website": {
        "summary": "Portfolio website with CMS-driven content, analytics, accessibility checks, and automated previews.",
        "entry": "CDN/Edge",
        "core": "Static Site + API",
        "data": "CMS/Assets",
        "queue": "Build/Webhook Queue",
    },
}

base_sections = dedent(
    """
    ## Executive Summary
    - **Overview:** {summary}
    - **Business Impact:** Accelerates delivery with standardized patterns, reduces operational risk, and improves customer trust through reliability and compliance.
    - **Technical Value Proposition:** Modular reference implementation with IaC, immutable delivery, and built-in observability and security controls.
    - **Success Metrics & KPIs:** Deployment lead time <30 minutes, change failure rate <5%, p95 latency targets per SLO, and availability >=99.9%.

    ## README / Setup & Deployment
    1. **Prerequisites:** Docker, Terraform, language runtime (Python/Node/Go), package manager, and cloud CLI configured with least-privileged credentials.
    2. **Bootstrap:** `make install` to fetch deps; `make lint test` locally; copy `.env.example` to `.env` with secrets managed via Vault/KMS.
    3. **Run Locally:** `make dev` to start services plus `make seed` where data fixtures exist.
    4. **Provision:** `terraform init && terraform apply` in `infra/` to stand up foundational resources.
    5. **Deploy:** CI/CD pipeline builds containers, signs artifacts, pushes to registry, applies manifests/Helmfile, and runs smoke + health checks before cutover.

    ## Architecture Diagram Pack
    ```mermaid
    flowchart TD
        User[Users/Clients] --> Entry[{entry}]
        Entry --> Core[{core}]
        Core --> Data[{data}]
        Core --> Queue[{queue}]
        Core --> Obs[Observability]
        Obs --> Dash[Dashboards/Alerts]
    ```

    ASCII topology:
    ```
    [User/Client]
        | HTTPS/API
    [{entry}]
        | service mesh / authn
    [{core}] -- telemetry --> [Observability]
        | stateful I/O
    [{data}] <= replication => backups
        | async
    [{queue}] -> workers
    [Dashboards/Alerts]
    ```

    ## Data Flow & Deployment Topology
    - Ingress authenticates, rate-limits, and forwards to core services behind a mesh with mTLS and policy enforcement.
    - Core services perform business logic, emit structured logs/traces, and interact with data stores via ORM/DAO layers.
    - Async queue offloads heavy tasks; workers scale horizontally; retries and DLQs handle poison messages.
    - Multi-env topology: **dev** (ephemeral), **stage** (pre-prod with load testing), **prod** (multi-AZ/region where applicable) with GitOps reconciliation.

    ## Code Generation Prompts
    - **Infrastructure as Code:** "Generate Terraform for {entry} + {core} + {data}, with variables, remote state, and workspace-per-env. Include security groups, IAM roles, KMS encryption, backups, and autoscaling policies."
    - **Backend Service:** "Scaffold a {core}-aligned service with REST/GraphQL endpoints, persistence adapters for {data}, and OpenTelemetry instrumentation. Include health/readiness probes and structured logging."
    - **Frontend/Components:** "Create a UI/workflow surfacing {summary_lower} KPIs with role-based views, responsive design, and accessibility AA compliance."
    - **Containerization:** "Produce Dockerfile and Helm chart/K8s manifests with non-root user, resource requests/limits, liveness/readiness probes, and secret mounting via CSI." 
    - **CI/CD Pipelines:** "Build GitHub Actions/GitLab CI that runs lint+tests, builds SBOM, signs images (cosign), pushes to registry, applies IaC/manifests, and gates on policy checks."
    - **Observability Instrumentation:** "Add OTEL SDK, propagate tracecontext, emit RED metrics, and expose `/metrics` for Prometheus plus log correlation IDs."

    ## Testing Suite
    - **Strategy:** Shift-left with unit, contract, integration, e2e, security, and performance gates; use ephemeral preview environments per PR.
    - **Test Plan:** Verify CRUD/API correctness, idempotent IaC, failure/retry paths, and data integrity across {data}.
    - **Test Cases & Acceptance:** Define Gherkin scenarios for critical user journeys; acceptance requires zero critical defects, latency within SLO, and successful rollback drills.
    - **API Testing:** Collections for authn/authz, pagination, validation errors, and idempotency keys.
    - **Security Testing:** SAST, DAST, dependency scanning, container scanning, secrets detection, and IaC policy checks (OPA/Sentinel).
    - **Performance:** Load tests simulating peak traffic with autoscaling verification and circuit-breaker behavior.
    - **CI Quality Gates:** Coverage >=80%, lint blockers resolved, and no critical vulnerabilities.

    ## Operational Documents
    - **Operational Playbook:** Daily checks on error budgets, capacity, and security posture; weekly chaos drills where applicable.
    - **Runbook:** Incident response with triage (severity mapping), containment, mitigation, communication templates, and postmortem timeline capture.
    - **SOP:** Access requests, change management approvals, and backup/restore procedures with RPO/RTO targets.
    - **On-Call & Escalation:** Primary/secondary rotation, pager rules, and vendor contact list; time-to-ack <5 minutes.
    - **Data Migration Runbook:** Pre-migration validation, dual-write toggle, backfill, checksum verification, and cutover with rollback switch.

    ## Reporting Package
    - Status report template (milestones, risks, blockers, scope changes).
    - KPI/OKR tracker covering deployment velocity, reliability, cost, and security findings.
    - Findings/recommendations report aligned to audits and retrospectives.
    - ROI analysis with payback period, efficiency gains, and risk reduction.
    - Timeline with milestones, gates, and owner assignments.

    ## Metrics & Observability
    - **SLO/SLI:** Availability >=99.9%, p95 latency targets, error rate <0.1%, throughput targets per project domain.
    - **PromQL Examples:**
      - `histogram_quantile(0.95, sum by (le,service) (rate(http_request_duration_seconds_bucket[5m])))`
      - `sum by (service) (rate(http_requests_total{{status=~"5.."}}[5m])) > 0`
      - `avg_over_time(queue_depth[5m]) > 100` triggers scaling/alerts.
    - **Dashboards:** RED + USE views, release markers, capacity heatmaps, and user journey funnels.
    - **Logging/Tracing:** JSON logs with trace/span IDs; OTLP exporters to collector; sampling tuned per env.

    ## Security Package
    - **Threat Model (STRIDE):** Spoofing (mTLS/JWT), Tampering (signatures, immutability), Repudiation (audit logs), Information Disclosure (encryption in transit/at rest), Denial of Service (WAF/rate limits/autoscale), Elevation of Privilege (RBAC/least privilege).
    - **Access Control & RBAC:** Principle-of-least-privilege roles, break-glass accounts, and just-in-time elevation.
    - **Encryption & Keys:** KMS/Key Vault for data at rest; TLS 1.2+/HSTS; key rotation with audit trails.
    - **Secrets Management:** Vault/Secrets Manager with short-lived tokens and sealed backups.
    - **Compliance Mapping:** Controls for SOC2/ISO 27001 covering logging, backup, change management, and vulnerability management.

    ## Risk Management
    - Risks: supply-chain compromise, misconfiguration, data loss, performance regressions, capacity exhaustion, key leakage, cost overrun, incident fatigue, vendor lock-in, and schema drift.
    - Mitigations: signed artifacts, policy-as-code, tested backups, perf tests + autoscaling, secrets hygiene, budget alerts, runbook rotations, and multi-cloud abstractions where feasible.
    - Owners: Tech Lead (engineering risks), SRE (reliability), Security (compliance), Product (cost/scope).
    - Residual risk assessed monthly with scorecards.

    ## Architecture Decision Records
    - **ADR-001:** Choose IaC (Terraform) for repeatability and policy enforcement.
    - **ADR-002:** Adopt GitOps for environment drift detection and auditable changes.
    - **ADR-003:** Standardize observability with OTEL and Prometheus-compatible stack.
    - **ADR-004:** Enforce trunk-based development with feature flags and progressive delivery.
    - **ADR-005:** Prefer managed services for core dependencies to reduce ops toil.

    ## Business Value Narrative
    - **Business Case:** {summary}
    - **Recruiter-Ready Angle:** Demonstrates ability to design, secure, and operate production-grade systems with measurable outcomes.
    - **Skills Demonstrated:** Cloud architecture, automation, security, observability, testing at scale, and stakeholder communication.
    - **Career Relevance:** Highlights end-to-end ownership from design through operations and continuous improvement.
    """
)

projects_dir = os.path.join(os.getcwd(), "projects")

for slug, meta in projects.items():
    path = os.path.join(projects_dir, slug, "README.md")
    if not os.path.exists(path):
        continue
    content = base_sections.format(
        summary=meta["summary"],
        summary_lower=meta["summary"].lower(),
        entry=meta["entry"],
        core=meta["core"],
        data=meta["data"],
        queue=meta["queue"],
    ).lstrip()
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {meta['summary'].split(':')[0] if ':' in meta['summary'] else slug.replace('-', ' ').title()}\n\n" + content)

print("Updated", len(projects), "project READMEs")
