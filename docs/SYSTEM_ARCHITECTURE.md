# System Architecture

## 1. Executive Summary
This portfolio models an enterprise platform that spans frontend experiences, backend services, data streaming, analytics, AI, infrastructure-as-code, and security automation. Each project is intentionally decoupled yet interoperable through opinionated interfaces (REST, GraphQL, gRPC, events, and infrastructure modules). Together they demonstrate how a modern engineering organization builds resilient capabilities across the software lifecycle—from product delivery to operations and governance.

## 2. Platform Topology
The platform is organized into six macro-domains:

1. **Digital Experience** – Client applications (React, Blazor, Electron) consume APIs and present data visualizations.
2. **Application Services** – FastAPI, GraphQL, and Rust-based microservices deliver business logic, authentication, and compute-intensive workflows.
3. **Data & AI Fabric** – Kafka streaming, PySpark ETL, and ML pipelines capture, process, and serve intelligence back to services and users.
4. **Infrastructure & Platform Engineering** – Terraform, Helm, Docker, and GitOps assets provision the runtime substrates across AWS, Kubernetes, and local developer environments.
5. **Security & Compliance** – Policy-as-code, posture scanning, zero-trust networking, and disaster recovery strategy provide governance and guardrails.
6. **Operations & Observability** – Monitoring-as-code and backup utilities establish feedback loops for reliability engineering.

A high-level event-driven architecture ties these domains together:

- **Ingress** – Users interact via the React SPA, Blazor WASM component, Electron desktop app, or AI assistant UI.
- **Service Mesh** – Requests fan out to REST/GraphQL/Rust services hosted on Kubernetes or serverless runtimes.
- **Data Plane** – Services persist state in Firestore, DynamoDB, PostgreSQL, or stream through Kafka topics into data lakes processed by PySpark.
- **Intelligence Loop** – ML pipelines consume curated datasets and deploy models consumed by the AI assistant or backend APIs.
- **Observability Fabric** – Prometheus/Grafana stack collects metrics/logs/traces from every workload; posture scanners and policy enforcement feed SecOps dashboards.

## 3. Domain Interaction Map
| Producer | Interface | Consumer | Notes |
| --- | --- | --- | --- |
| React To-Do App | HTTPS (REST) | FastAPI Backend | CRUD workflows, authentication, realtime updates mirrored via Firestore webhooks. |
| FastAPI Backend | Kafka Topic `events.tasks` | Kafka Producer/Consumer | Emits audit events for downstream analytics, consumed by ETL and ML pipelines. |
| Kafka Producer | gRPC/gateway | Kafka Cluster | Seeds synthetic streaming data for load and resiliency testing. |
| Kafka Consumer | REST webhook | Monitoring Stack | Pushes processing metrics and alerts to Prometheus pushgateway. |
| Terraform Modules | Terraform Cloud / CLI | AWS Accounts | Provision S3 static site, VPC, and RDS with shared networking conventions. |
| Helm Chart | Helm Repository | Kubernetes Clusters | Deploys backend + monitoring workloads with opinionated defaults. |
| OPA Policies | Admission Controller | Kubernetes API Server | Enforces workload security baselines (namespace, labels, runtime class). |
| ML Ops Pipeline | GitHub Actions | Model Registry + Artifact Store | Automates training, evaluation, and deployment of ML models consumed by AI assistant. |
| Monitoring-as-Code | Docker Compose | Local Ops | Provides full observability lab replicating production dashboards locally. |
| Security Scanner | AWS APIs | SecOps Reporting | Continuously scans accounts for drift against security baseline; integrates with DR plan triggers. |

## 4. Environment Layout
| Environment | Purpose | Hosting | Git Strategy |
| --- | --- | --- | --- |
| **Local** | Developer workstation using Docker Compose, local Kafka, and mocked cloud services. | Docker Desktop/Podman, LocalStack | Feature branches off `work`, short-lived. |
| **Dev** | Shared integration environment with full CI/CD automation. | AWS dev account + EKS cluster | Branch `dev` (protected), deploys on merge. |
| **Staging** | Production-like validation environment with performance and security testing gates. | AWS staging account, RDS Multi-AZ, Kafka MSK | Branch `staging`, release candidates tagged. |
| **Production** | Customer-facing workloads with multi-region resilience. | AWS prod account, multi-region failover, CloudFront | Branch `main`, release via GitOps promotion. |

### Network Segmentation
- **Public Subnets** host API Gateways, ALBs, and Bastion hosts.
- **Private App Subnets** run EKS node groups, Lambda, and container workloads.
- **Private Data Subnets** isolate RDS, Kafka brokers, and Elasticache.
- **Security Services Subnet** runs inspection (NIDS), SIEM forwarders, and backup endpoints.

## 5. Cross-Cutting Concerns
### Identity & Access Management
- Centralized identity via AWS IAM Identity Center with SCIM provisioning to GitHub and Kubernetes RBAC.
- Service-to-service authentication uses JWTs signed by AWS KMS; workloads rotate secrets with AWS Secrets Manager.

### Observability
- Metrics scraped by Prometheus; Grafana dashboards versioned with provisioning code.
- Loki aggregates logs; Tempo traces instrumented via OpenTelemetry across services.
- Alertmanager routes to PagerDuty, Slack, and email with runbook annotations.

### Resilience & Data Protection
- Multi-AZ deployment for RDS; cross-region replication for S3 buckets.
- Kafka configured with 3x replication and rack awareness.
- Disaster recovery tests executed quarterly using the Enterprise DR Plan project.

### Security Guardrails
- OPA policies and AWS Config rules enforce tagging, encryption, and network controls.
- CI pipelines include SAST (Bandit, cargo audit), dependency scanning, and container image signing.
- Supply chain integrity via Sigstore Cosign and Terraform Cloud Sentinel policies.

## 6. Project Dependency Graph
```
frontend/react-firestore-todo → backend/fastapi-backend-api → data-streaming/kafka-data-producer
                                                                ↘ security/cloud-security-posture-scanner
backend/graphql-ariadne-api → data-streaming/kafka-data-consumer → big-data/pyspark-etl-job → ai-ml/ai-research-assistant
backend/rust-microservice ↗                                        ↘ devops/mlops-github-actions-pipeline
serverless/aws-serverless-api ↗                                      
monitoring/monitoring-as-code-compose ↘ orchestration/kubernetes-helm-chart ↘ security/opa-k8s-policy
iac/secure-vpc-infra → iac/rds-postgresql-infra → backend services
iac/terraform-s3-static-site → frontend static hosting → CDN edge security
strategy/disaster-recovery-plan ties into every project for failover readiness
```

## 7. Delivery & Governance
- **Git Monorepo** with CODEOWNERS enforcing review boundaries per domain.
- **CI/CD** orchestrated via reusable GitLab & GitHub Actions workflows.
- **Change Management** uses ADRs stored alongside project documentation; updates require architecture review sign-off.

## 8. Roadmap & Extensibility
- Extend data mesh capabilities via additional domain-driven Kafka topics.
- Expand Zero Trust posture with service mesh (Istio) for mTLS enforcement.
- Enhance AI assistant with retrieval-augmented generation pipelines using vector stores.
- Introduce FinOps dashboards combining cost explorer data with workload metrics.

## 9. Reference Artifacts
- Diagrams (C4 + sequence) stored in `docs/diagrams/` (future expansion) with PlantUML + Mermaid sources.
- ADRs in each project folder capture context-specific decisions.
- Operations runbooks located in the `operations/` subfolders per project.

