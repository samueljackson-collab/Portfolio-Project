# Master Artifacts

- **Terraform environments**: `infrastructure/terraform/environments/main.tf` with dev/staging/prod variables (`dev.tfvars`, `staging.tfvars`, `prod.tfvars`) and shared inputs in `variables.tf`.
- **Ansible automation**: inventory and playbook driven role in `infrastructure/ansible` (hosts, group vars, `playbooks/site.yml`, orchestration role templates).
- **Orchestration service & API**: FastAPI router and service in `backend/app/routers/orchestration.py`, `backend/app/services/orchestration_service.py`, with schemas/tests in `backend/app/schemas.py` and `backend/tests/test_orchestration.py`.
- **React operations console**: protected UI at `/operations` implemented in `frontend/src/pages/OrchestrationConsole.tsx`, wired through `frontend/src/App.tsx`, API types/services in `frontend/src/api`.
- **Container/Kubernetes delivery**: Docker compose stack in `deploy/docker-compose.operations.yml` and Kubernetes manifests in `deploy/k8s` (`backend.yaml`, `frontend.yaml`, `observability.yaml`).
- **CI pipeline**: GitHub Actions workflow `.github/workflows/platform-ci.yml` covering backend tests, frontend build, Terraform, and Ansible linting.
- **Observability assets**: OTel collector config `observability/otel-collector.yaml`, Grafana provisioning and dashboard JSON in `observability/grafana`, and operational guidance in `docs/runbooks/observability-runbook.md`.
- **Runbooks & diagrams**: Orchestration procedure `docs/runbooks/orchestration-runbook.md` with the accompanying architecture diagram `docs/diagrams/orchestration-architecture.md` and MASTER_ARTIFACTS cross-links.
