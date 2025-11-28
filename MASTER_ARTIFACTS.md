# Master Artifacts

- **Infrastructure**: Terraform root stack and variables for VPC, ECS, and RDS in `infrastructure/terraform/main.tf`, `variables.tf`, and `terraform.tfvars.example`. Kubernetes deployment bundle is in `infrastructure/kubernetes/portfolio-stack.yaml`, and Docker Compose for local orchestration sits at `docker/portfolio-compose.yml`.
- **Configuration Management**: Ansible inventory, group vars, and role-based playbook in `infrastructure/ansible` (`playbooks/site.yml` plus `roles/common`, `roles/backend`, `roles/orchestrator`, `roles/frontend`).
- **Orchestration Service**: FastAPI orchestration router and in-memory store at `backend/app/routers/orchestration.py` with coverage in `backend/tests/test_orchestration.py`.
- **React Console**: Orchestration console UI, routes, and API wiring in `frontend/src/pages/OrchestrationConsole.tsx`, `frontend/src/App.tsx`, `frontend/src/api/services.ts`, and `frontend/src/api/types.ts` with navigation hook-ups in `frontend/src/components/Navbar.tsx`.
- **Pipelines**: GitHub Actions CI across backend, frontend, Terraform, and Ansible in `.github/workflows/ci.yml`.
- **Observability**: OTEL collector pipeline in `observability/otel-collector.yaml`, Grafana dashboard definition at `observability/grafana-dashboard.json`, and architecture diagram in `docs/diagrams/portfolio-orchestration.md`.
- **Runbooks**: Operational guidance for the orchestration console and APIs in `docs/runbooks/orchestration-runbook.md`.
