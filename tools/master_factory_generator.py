import textwrap
from pathlib import Path

projects = [
    {
        "id": "P01",
        "slug": "p01-aws-infra",
        "name": "AWS Infrastructure Automation",
        "summary": "CloudFormation and Terraform automation for VPC, RDS, and disaster recovery drills.",
        "domain": "Cloud infrastructure",
        "workloads": ["VPC networking", "RDS databases", "DR drill scripts"],
        "ci": "GitHub Actions -> lint -> unit tests -> terraform plan -> CloudFormation change sets -> gated apply",
        "iac": "Terraform modules for network + CloudFormation templates for RDS with S3 backend state",
    },
    {
        "id": "P02",
        "slug": "p02-iam-hardening",
        "name": "IAM Security Hardening",
        "summary": "Least-privilege policy packs, Access Analyzer automation, and credential hygiene tooling.",
        "domain": "Security automation",
        "workloads": ["IAM policy baselines", "Access Analyzer jobs", "credential rotation"],
        "ci": "GitHub Actions -> policy linting -> unit tests -> drift detection -> deploy via Terraform",
        "iac": "Terraform for IAM roles, SCP samples, and analyzer configurations",
    },
    {
        "id": "P03",
        "slug": "p03-hybrid-network",
        "name": "Hybrid Network Connectivity",
        "summary": "WireGuard/IPsec lab with benchmarking and BGP-ready design for hybrid clouds.",
        "domain": "Networking",
        "workloads": ["WireGuard peers", "IPsec tunnels", "Latency benchmarking"],
        "ci": "CI -> lint -> integration emulation -> publish connection profiles",
        "iac": "Ansible playbooks and Terraform for gateway provisioning",
    },
    {
        "id": "P04",
        "slug": "p04-ops-monitoring",
        "name": "Operational Monitoring Stack",
        "summary": "Prometheus, Grafana, and Alertmanager bundle with remediation hooks.",
        "domain": "Monitoring",
        "workloads": ["Prometheus scrape configs", "Grafana dashboards", "Alertmanager routes"],
        "ci": "CI -> lint configs -> container build -> smoketest dashboards -> push to registry",
        "iac": "Docker Compose and Kubernetes manifests for observability services",
    },
    {
        "id": "P05",
        "slug": "p05-mobile-testing",
        "name": "Mobile App Manual Testing",
        "summary": "Charters, device matrix, and regression checklists with evidence capture guidance.",
        "domain": "Quality assurance",
        "workloads": ["Exploratory charters", "Device coverage matrix", "Regression packs"],
        "ci": "CI -> lint markdown -> aggregate test notes -> publish artifacts",
        "iac": "Not applicable; config driven test assets with optional Device Farm definitions",
    },
    {
        "id": "P06",
        "slug": "p06-e2e-testing",
        "name": "Web App Automated Testing",
        "summary": "Playwright E2E suite with desktop and mobile coverage and Make-driven CI hooks.",
        "domain": "Test automation",
        "workloads": ["Playwright specs", "Mock data fixtures", "Headless CI runs"],
        "ci": "GitHub Actions -> npm lint -> playwright test -> upload traces -> publish report",
        "iac": "Dockerfile for runner plus optional k8s Job for scheduled suites",
    },
    {
        "id": "P07",
        "slug": "p07-roaming-simulation",
        "name": "International Roaming Simulation",
        "summary": "Python simulator for roaming scenarios with pytest coverage and metrics export hooks.",
        "domain": "Telecom simulation",
        "workloads": ["Roaming events", "Packet traces", "Metrics export"],
        "ci": "CI -> lint -> pytest -> package CLI -> publish container",
        "iac": "Terraform to provision lab VMs and S3 log buckets",
    },
    {
        "id": "P08",
        "slug": "p08-api-testing",
        "name": "Backend API Testing",
        "summary": "Postman collections and Newman harness for regression and latency baselines.",
        "domain": "API quality",
        "workloads": ["Postman collections", "Environment configs", "Latency baselines"],
        "ci": "CI -> collection lint -> newman smoke -> publish junit -> push evidence",
        "iac": "Docker Compose for mock services and load generators",
    },
    {
        "id": "P09",
        "slug": "p09-cloud-native-poc",
        "name": "Cloud-Native POC",
        "summary": "FastAPI microservice with container build, pytest coverage, and Kubernetes manifests.",
        "domain": "Application platform",
        "workloads": ["FastAPI service", "Container image", "Kubernetes deployment"],
        "ci": "CI -> lint -> pytest -> build image -> scan -> push -> deploy to kind",
        "iac": "Terraform for cluster bootstrap plus Helm/K8s manifests",
    },
    {
        "id": "P10",
        "slug": "p10-multi-region",
        "name": "Multi-Region Architecture",
        "summary": "Active/passive AWS blueprint with Route 53 failover and replication tests.",
        "domain": "Resilience",
        "workloads": ["Route53 health checks", "Replication", "Failover automation"],
        "ci": "CI -> terraform validate -> plan -> simulated failover tests -> approval -> apply",
        "iac": "Terraform for regional stacks and S3/DB replication",
    },
    {
        "id": "P11",
        "slug": "p11-serverless",
        "name": "API Gateway & Serverless",
        "summary": "SAM-driven Lambda stack with DynamoDB data layer and observability hooks.",
        "domain": "Serverless",
        "workloads": ["Lambda handlers", "API Gateway", "DynamoDB tables"],
        "ci": "CI -> sam validate -> unit tests -> sam build -> deploy to dev -> canary tests",
        "iac": "AWS SAM/CloudFormation templates",
    },
    {
        "id": "P12",
        "slug": "p12-data-pipeline",
        "name": "Data Pipeline (Airflow)",
        "summary": "Dockerized Airflow with ETL DAGs and dataset snapshots for promotions.",
        "domain": "Data engineering",
        "workloads": ["Airflow DAGs", "ETL tasks", "Data quality checks"],
        "ci": "CI -> dag lint -> pytest -> airflow dag validation -> build image -> deploy",
        "iac": "Docker Compose and Terraform for Airflow infra",
    },
    {
        "id": "P13",
        "slug": "p13-ha-webapp",
        "name": "High-Availability Web App",
        "summary": "NGINX load balancer with replicated app tier and DB replication via Compose.",
        "domain": "HA web platform",
        "workloads": ["NGINX LB", "App replicas", "Database replication"],
        "ci": "CI -> lint -> unit/integration tests -> docker build -> HA simulation -> push",
        "iac": "Docker Compose + optional Terraform for VM hosts",
    },
    {
        "id": "P14",
        "slug": "p14-disaster-recovery",
        "name": "Disaster Recovery",
        "summary": "Backup scripts with RPO/RTO runbooks and restore drill automation.",
        "domain": "Business continuity",
        "workloads": ["Database backups", "Restore drills", "RPO/RTO tracking"],
        "ci": "CI -> lint -> backup script unit tests -> restore simulations -> report upload",
        "iac": "Terraform for backup storage and IAM roles",
    },
    {
        "id": "P15",
        "slug": "p15-cost-optimization",
        "name": "Cloud Cost Optimization",
        "summary": "Athena CUR queries, FinOps scripts, and dashboards for savings plans.",
        "domain": "FinOps",
        "workloads": ["CUR ingestion", "Savings plan analysis", "Forecasting"],
        "ci": "CI -> lint -> unit tests -> dry-run queries -> publish cost reports",
        "iac": "Terraform for Athena, Glue catalog, and S3 buckets",
    },
    {
        "id": "P16",
        "slug": "p16-zero-trust",
        "name": "Zero-Trust Architecture",
        "summary": "Policy templates, cert automation, and threat models for zero-trust enforcement.",
        "domain": "Security architecture",
        "workloads": ["mTLS", "Policy evaluation", "Microsegmentation"],
        "ci": "CI -> policy lint -> unit tests -> conftest -> package bundles -> deploy",
        "iac": "Terraform for PKI, gateways, and policy stores",
    },
    {
        "id": "P17",
        "slug": "p17-terraform-multicloud",
        "name": "Terraform Multi-Cloud",
        "summary": "Shared modules for AWS/Azure with CI hooks and workspace examples.",
        "domain": "IaC platform",
        "workloads": ["Shared modules", "Remote state", "Workspace promotion"],
        "ci": "CI -> terraform fmt/validate -> tflint -> terratest -> plan -> apply",
        "iac": "Terraform modules and environment stacks",
    },
    {
        "id": "P18",
        "slug": "p18-k8s-cicd",
        "name": "CI/CD + Kubernetes",
        "summary": "kind-based dev cluster, GitHub Actions workflow, and Kubernetes manifests.",
        "domain": "CI/CD & K8s",
        "workloads": ["GitHub Actions", "K8s manifests", "Blue/green rollout"],
        "ci": "CI -> lint -> unit tests -> build/push images -> deploy to kind -> e2e",
        "iac": "Terraform for registries + k8s manifests/Helm charts",
    },
    {
        "id": "P19",
        "slug": "p19-security-automation",
        "name": "Cloud Security Automation",
        "summary": "CIS compliance scanner and remediation playbooks with GuardDuty integration.",
        "domain": "Security automation",
        "workloads": ["CIS scanning", "GuardDuty hooks", "Remediation playbooks"],
        "ci": "CI -> static analysis -> unit tests -> scan dry-runs -> artifact publish",
        "iac": "Terraform for scanners, EventBridge, and remediation lambdas",
    },
    {
        "id": "P20",
        "slug": "p20-observability",
        "name": "Observability Engineering",
        "summary": "Prometheus/Grafana/Loki configs with dashboards and alerting playbooks.",
        "domain": "Observability",
        "workloads": ["Metrics pipelines", "Logs ingestion", "Alerting routes"],
        "ci": "CI -> lint configs -> container build -> synthetic checks -> push dashboards",
        "iac": "Terraform for monitoring stack and S3 artifact buckets",
    },
]

def render_diagrams(p):
    mermaid = f"""```mermaid
flowchart LR
    dev[Developers] --> ci[CI Pipeline\\n({p['ci']})]
    ci --> build[Build & Verify]
    build --> scans[Security Scans]
    scans --> registry[(Artifacts/Registry)]
    registry --> deploy{{Deploy}}
    deploy --> iac[IaC: {p['iac']}]
    deploy --> runtime[{p['name']} Runtime]
    runtime --> obs[Observability Stack]
    obs --> reports[Reports & KPIs]
```
"""
    ascii = textwrap.dedent(f"""
    ASCII CI/CD + IaC Topology
    ---------------------------
    [Developers]
         |
    [CI: {p['ci']}]
         |--> Build/Test
         |--> Security Scans
         v
    [Artifact Registry]
         |
    [Deploy Orchestrator]
         |--> IaC apply: {p['iac']}
         |--> Service rollout: {p['name']} components
         v
    [Monitoring/Logging] --> [Reports/KPIs]
    """)
    return mermaid, ascii

def render_file(p):
    mermaid, ascii = render_diagrams(p)
    workloads = "\n".join(f"- {w}" for w in p["workloads"])
    content = f"""# {p['id']} – {p['name']} Master Factory Deliverable

## 1. README / Overview
- **Domain:** {p['domain']}
- **Objective:** {p['summary']}
- **Key Workloads:**\n{workloads}
- **Execution Hooks:** Make targets reference CI steps: {p['ci']}.

## 2. Architecture & IaC Diagrams
### Mermaid
{mermaid}
### ASCII
{ascii}

## 3. CI/CD Blueprint
- Pipeline: {p['ci']}.
- Stages: plan, security scan, automated tests, artifact push, and environment promotion with manual approval for production.
- Evidence: pipeline publishes JUnit, coverage, security SARIF, and deployment change sets.

## 4. Code Prompts & Generation Guardrails
- **Implementation prompt:** "Implement the {p['name']} feature with infrastructure alignment: respect existing interfaces, add tests, and ensure lint passes."
- **Review checklist prompt:** "Audit {p['id']} changes for security, performance, observability, and backward compatibility before merge."
- **IaC prompt:** "Generate Terraform/CloudFormation blocks consistent with {p['iac']} and tag resources with owner, env, and cost-center."

## 5. Testing Suite
- Unit tests cover core logic and configuration parsing.
- Integration tests validate {", ".join(p['workloads'])} across dev/stage.
- Performance checks ensure SLOs remain within thresholds (latency, throughput, or coverage as applicable).
- CI artifacts include traces/screenshots for regressions.

## 6. Operations & Runbooks
- Daily health checks: verify service uptime, dependency status, and alert queue emptiness.
- Deployment runbook: trigger pipeline, review plan, approve deploy, and verify dashboards post-release.
- Incident flow: triage -> mitigate -> root cause -> retrospective with linked ADR updates.

## 7. Reporting & Analytics
- KPIs: delivery lead time, change failure rate, mean time to detect/recover, and domain-specific metrics.
- Dashboards compile pipeline history, coverage trends, and capacity utilization.
- Weekly report template pulls from CI metadata and observability events.

## 8. Observability
- Metrics: export Prometheus/OpenTelemetry counters for success/failure, latency, and resource usage.
- Logs: structured JSON with correlation IDs; shipped to centralized stack referenced in configs.
- Traces: instrument key flows to capture dependencies and retries.

## 9. Security & Compliance
- Controls: least privilege, secret scanning, dependency auditing, and TLS in transit.
- Evidence: attach policy IDs, scan reports, and signed build manifests.
- Compliance hooks align with CIS/SOC2 requirements for the stack.

## 10. Risk Management
- Top risks: drift between IaC and runtime, misconfigured alerts, and untested failovers.
- Mitigations: automated drift detection, alert simulations, and quarterly game days.
- Residual risk tracked with owners and review cadence per release train.

## 11. Architecture Decision Records (ADRs)
- ADR-001: Platform choice for {p['name']} stack (Accepted).
- ADR-002: Security model and secrets handling (Accepted).
- ADR-003: Observability tooling and SLIs/SLOs (Proposed/Review).

## 12. Business Narrative & Outcomes
- Business value: accelerates {p['domain'].lower()} objectives with audit-ready artifacts.
- Stakeholder impact: clearer evidence for leadership, faster onboarding for engineers, and reusable templates across teams.
- Success metrics: adoption of automation, reduction in manual effort, and uptime/security improvements tied to KPIs.
"""
    return content

def main():
    for project in projects:
        target_dir = Path("projects") / project["slug"] / "master-factory"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "MASTER_FACTORY.md"
        target_file.write_text(render_file(project))

if __name__ == "__main__":
    main()
