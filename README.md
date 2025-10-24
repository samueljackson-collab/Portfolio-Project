# 🚀 Enterprise-Grade Technical Portfolio

A curated collection of 25 production-ready projects demonstrating senior-level expertise across cloud architecture, platform engineering, DevOps, security, AI, and modern software delivery. This monorepo is structured to mirror a real-world engineering organization with shared tooling, governance, and operational excellence.

> 📚 **Start here:**
> - [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
> - [Security Strategy](docs/SECURITY_STRATEGY.md)
> - [Deployment & Operations Guide](docs/DEPLOYMENT_GUIDE.md)

## 🎯 Portfolio Highlights
- Multi-cloud, multi-runtime coverage: React, FastAPI, Rust, GraphQL, serverless, and Kubernetes workloads.
- Infrastructure-as-code for networking, databases, and static hosting with Terraform and Helm.
- End-to-end DevSecOps with CI/CD pipelines, policy-as-code, observability stacks, and compliance automation.
- AI/ML, big data, and streaming examples connecting Kafka, PySpark, and ML pipelines to production services.
- Strategy and governance artifacts including disaster recovery, runbooks, and security posture reporting.

## 🗂️ Project Directory
| # | Project | Category | Description |
| --- | --- | --- | --- |
| 1 | [React To-Do List App with Firestore](projects/frontend/react-firestore-todo/) | Frontend | Real-time collaborative SPA with Firebase Auth, Firestore, and LaunchDarkly flags. |
| 2 | [Python FastAPI Backend API](projects/backend/fastapi-backend-api/) | Backend | Async REST API with PostgreSQL, Redis caching, Kafka event emission, and observability. |
| 3 | [DevOps File Backup Utility](projects/devops/file-backup-utility/) | DevOps | Idempotent backup automation with encryption, multi-target uploads, and reporting. |
| 4 | [Terraform S3 Static Website Bucket](projects/iac/terraform-s3-static-site/) | IaC | Secure CloudFront-backed static hosting with WAF and KMS encryption. |
| 5 | [Interactive Bar Chart with D3.js](projects/data-viz/d3-interactive-bar-chart/) | Data Viz | Accessible D3 visualization component packaged for React dashboards. |
| 6 | [CI/CD Pipeline for Backend API](projects/devops/cicd-backend-pipeline/) | CI/CD | GitLab pipeline templates covering linting, testing, security, and GitOps deployment. |
| 7 | [Optimized Dockerfile for FastAPI App](projects/devops/dockerfile-fastapi/) | Containerization | Multi-stage Dockerfile with supply-chain hardening and BuildKit optimizations. |
| 8 | [Kubernetes Helm Chart](projects/orchestration/kubernetes-helm-chart/) | Orchestration | Opinionated Helm chart for stateless microservices with autoscaling and monitoring. |
| 9 | [OPA Security Policy for Kubernetes](projects/security/opa-k8s-policy/) | Security | Gatekeeper policy bundle enforcing pod security, labeling, and registry trust. |
| 10 | [Kafka Data Producer](projects/data-streaming/kafka-data-producer/) | Data Streaming | Async producer generating workload profiles and emitting metrics. |
| 11 | [Kafka Data Consumer](projects/data-streaming/kafka-data-consumer/) | Data Streaming | Transform-and-forward consumer with DLQ handling and observability. |
| 12 | [AI Research Assistant with Grounding](projects/ai-ml/ai-research-assistant/) | AI / ML | RAG chatbot combining Google Search grounding, moderation, and analytics. |
| 13 | [Serverless API Infrastructure](projects/serverless/aws-serverless-api/) | Serverless | Lambda/API Gateway stack with DynamoDB, EventBridge, and IaC automation. |
| 14 | [RDS PostgreSQL Database Infrastructure](projects/iac/rds-postgresql-infra/) | Database IaC | Multi-AZ PostgreSQL deployment with IAM auth, backups, and monitoring. |
| 15 | [Secure Cloud Network (VPC) Infrastructure](projects/iac/secure-vpc-infra/) | Networking IaC | Zero-trust VPC baseline with segmentation, endpoints, and firewall policies. |
| 16 | [Monitoring-as-Code Docker Compose](projects/monitoring/monitoring-as-code-compose/) | Observability | Prometheus, Grafana, Loki, Tempo stack codified for local parity and CI checks. |
| 17 | [Electron Desktop App](projects/desktop/electron-desktop-app/) | Desktop | Offline-first administration app with secure IPC and auto-update pipeline. |
| 18 | [Web3 Simple Smart Contract](projects/web3/simple-smart-contract/) | Web3 | Solidity ERC-20 reward token with Hardhat tests and security tooling. |
| 19 | [GraphQL API with Ariadne](projects/backend/graphql-ariadne-api/) | Backend | Schema-first GraphQL service with subscriptions, persisted queries, and federation hooks. |
| 20 | [MLOps CI/CD Pipeline with GitHub Actions](projects/devops/mlops-github-actions-pipeline/) | MLOps | Automated data validation, training, evaluation, and deployment workflows. |
| 21 | [Big Data ETL Job with PySpark](projects/big-data/pyspark-etl-job/) | Big Data | Airflow/Glue ETL pipeline with Great Expectations data quality and Delta Lake outputs. |
| 22 | [Cloud Security Posture Scanner](projects/security/cloud-security-posture-scanner/) | Security | AWS misconfiguration scanner with rule packs, reporting, and remediation workflows. |
| 23 | [High-Performance Rust Microservice](projects/backend/rust-microservice/) | Backend | Axum/Tonic service delivering low-latency compute with Prometheus/OTEL instrumentation. |
| 24 | [Blazor WebAssembly Counter Component](projects/frontend/blazor-webassembly-counter/) | Frontend | .NET 8 micro-frontend with SignalR sync and production build pipeline. |
| 25 | [Enterprise Disaster Recovery Plan](projects/strategy/disaster-recovery-plan/) | Strategy | RTO/RPO matrix, runbooks, exercises, and governance artifacts for platform resilience. |

## 🧭 Navigating the Monorepo
- Each project includes `README.md`, optional `docs/` for ADRs and diagrams, `ops/runbook.md`, and IaC/application code folders.
- Shared conventions, branching model, and promotion process are defined in the [Deployment & Operations Guide](docs/DEPLOYMENT_GUIDE.md).
- Security controls, identity strategy, and compliance mapping live in the [Security Strategy](docs/SECURITY_STRATEGY.md).
- Architectural views, integration topology, and dependency graph reside in the [System Architecture](docs/SYSTEM_ARCHITECTURE.md).

## 🤝 Contribution Workflow
1. Review architecture and security docs to understand context.
2. Open an issue outlining scope, success criteria, and validation steps.
3. Create feature branches using `<domain>/<issue-id>-short-description` naming convention.
4. Follow per-project lint/test instructions before opening a PR.
5. Ensure documentation and runbooks remain accurate after changes.

## 📬 Contact
Questions or collaboration ideas? Reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

