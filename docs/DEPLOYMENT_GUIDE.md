# Deployment & Operations Guide

## 1. Introduction
This guide describes how to bootstrap local environments, promote changes through dev → staging → production, and operate the portfolio long term. Each project contains its own runbook; this document stitches them together for platform engineers and program managers.

## 2. Repository Structure
```
Portfolio-Project/
├── README.md
├── docs/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── SECURITY_STRATEGY.md
│   └── DEPLOYMENT_GUIDE.md (this file)
└── projects/
    ├── frontend/
    │   ├── react-firestore-todo/
    │   └── blazor-webassembly-counter/
    ├── backend/
    │   ├── fastapi-backend-api/
    │   ├── graphql-ariadne-api/
    │   └── rust-microservice/
    ├── devops/
    │   ├── file-backup-utility/
    │   ├── cicd-backend-pipeline/
    │   ├── dockerfile-fastapi/
    │   └── mlops-github-actions-pipeline/
    ├── iac/
    │   ├── terraform-s3-static-site/
    │   ├── rds-postgresql-infra/
    │   └── secure-vpc-infra/
    ├── orchestration/
    │   ├── kubernetes-helm-chart/
    │   └── opa-k8s-policy/
    ├── data-streaming/
    │   ├── kafka-data-producer/
    │   └── kafka-data-consumer/
    ├── ai-ml/ai-research-assistant/
    ├── serverless/aws-serverless-api/
    ├── data-viz/d3-interactive-bar-chart/
    ├── monitoring/monitoring-as-code-compose/
    ├── desktop/electron-desktop-app/
    ├── web3/simple-smart-contract/
    ├── big-data/pyspark-etl-job/
    ├── security/
    │   └── cloud-security-posture-scanner/
    └── strategy/disaster-recovery-plan/
```
> **Note:** Each project folder contains a README, ADR folder, and optional `infra/`, `app/`, or `ops/` subdirectories depending on scope.

## 3. Tooling Prerequisites
| Tool | Version | Purpose |
| --- | --- | --- |
| Git | 2.40+ | Version control |
| Node.js | 18 LTS | Frontend builds, CDK scripts |
| Python | 3.11 | Backend services, automation |
| Rust | 1.74 | High-performance microservice |
| Go | 1.21 | Optional tooling (OPA compilation, CLI helpers) |
| Terraform | 1.6 | IaC deployments |
| AWS CLI | 2.x | Cloud operations |
| Docker | 24+ | Container builds & local runtime |
| Kubectl | 1.28 | Kubernetes management |
| Helm | 3.13 | Packaging workloads |
| Kafka CLI | 3.6 | Manage streaming topics |
| PySpark | 3.5 | Big data ETL |
| Poetry | 1.6 | Python dependency management |

## 4. Local Environment Bootstrap (Deployment Guide §13)
1. Clone repository and checkout `work` branch.
2. Install prerequisites (Node via fnm/nvm, Python via pyenv, etc.).
3. Run `make bootstrap` (future enhancement) or execute per-project setup scripts referenced in each README.
4. Start shared dependencies using `docker compose -f projects/monitoring/monitoring-as-code-compose/docker-compose.yml up -d` and `docker compose -f projects/data-streaming/kafka-data-producer/compose.kafka.yml up -d`.
5. Export environment variables from `env/local.example` (to be generated) using `direnv` or `dotenv` CLI.
6. Validate toolchain via `./scripts/validate-local.sh` (to be added) ensuring lint/test pass for critical services.

## 5. Branching & Release Strategy
- **work** – Default integration branch for contributors. Feature branches branch off here.
- **dev** – Continuous delivery branch managed by automation. Merge from `work` after passing integration tests.
- **staging** – Release candidate branch; deployments require security scans and manual approval.
- **main** – Production branch. Tag releases (`vYYYY.MM.DD`) and promote via GitOps.
- **Hotfixes** – Branch from `main`, apply fix, merge back to `main` and `work`.

## 6. CI/CD Overview
| Stage | Tools | Description |
| --- | --- | --- |
| **Lint & Static Analysis** | ESLint, Flake8, Cargo fmt, Terraform fmt/validate | Ensure code quality and formatting. |
| **Unit & Component Tests** | Jest, PyTest, Cargo test, Go test | Run per-project automated tests. |
| **Integration Tests** | Postman/Newman suites, PyTest integration, Cypress | Execute against dockerized stack.
| **Security Scans** | SAST, dependency scanning, Trivy image scan, OPA unit tests | Evaluate vulnerabilities and policy compliance. |
| **Build & Package** | Docker Buildx, Terraform plan, Helm package | Produce deployable artifacts and IaC plans. |
| **Deploy** | Argo CD, Terraform apply, Serverless Framework | Promote to target environments with approval gates. |
| **Post-Deploy Verification** | Synthetic monitoring, smoke tests, log/metric validation | Confirm health before release sign-off. |

Reusable pipeline templates stored in `projects/devops/cicd-backend-pipeline/.ci/templates/` (to be populated) accelerate adoption across services.

## 7. Environment Promotion Workflow
1. Developer merges feature branch → `work` triggers CI.
2. Automated PR merges from `work` → `dev` after green build; Argo CD syncs dev cluster.
3. Release manager schedules staging promotion, reviews Terraform plans, executes integration test suite.
4. Security & QA sign off; change advisory board (CAB) approves production release.
5. Git tag created; GitOps pipeline promotes manifests to production clusters/accounts.
6. Post-deploy review held within 24h to capture metrics and retro items.

## 8. Configuration Management
- **Secrets** – Managed via SOPS + age encryption. Encrypted files stored in repo under `secrets/` (future). Decryption requires age keys from secret manager.
- **Parameters** – Environment-specific `values.<env>.yaml` for Helm charts. Terraform uses workspaces with remote state (S3 + DynamoDB lock).
- **Feature Flags** – LaunchDarkly toggles stored in `ops/feature-flags.md` per project.

## 9. Operational Runbooks
Every project includes an `ops/runbook.md` file with:
- Service overview and ownership
- Monitoring dashboards and alert IDs
- Deploy/rollback procedure
- Common failure scenarios
- Support escalation ladder

The disaster recovery project curates master runbooks and links to per-service recovery steps.

## 10. Compliance & Audit Support
- Maintain change logs via conventional commits and release notes.
- Store evidence (plans, screenshots, test results) in `audits/<YYYY>/<control-id>/` per compliance cycle.
- Quarterly access reviews documented in `projects/security/cloud-security-posture-scanner/reports/`.

## 11. Contribution Workflow
1. Review `SYSTEM_ARCHITECTURE.md` and relevant project README for context.
2. Create issue with problem statement, success criteria, and acceptance tests.
3. Branch naming convention: `<domain>/<issue-id>-short-description` (e.g., `backend/123-add-pagination`).
4. Run `make lint test` (future aggregated script). Attach evidence to PR using checklist template.
5. Obtain approvals per CODEOWNERS; include security sign-off for sensitive changes.

## 12. Decommissioning & Sunsetting
- Initiate ADR to document rationale.
- Archive infrastructure (terraform destroy), remove from monitoring, update documentation.
- Preserve audit artifacts and backup snapshots for mandated retention.

## 13. Long-Term Governance
- Quarterly architecture reviews ensure platform coherence.
- Annual chaos engineering exercises validate DR readiness.
- Product council prioritizes roadmap alignment with business objectives.
- FinOps working group reviews cost efficiency, reserved instance usage, and rightsizing opportunities.

