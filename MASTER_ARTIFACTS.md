# Delivery Artifacts

- **Terraform blueprints:** `infrastructure/terraform/environments/staging` and `infrastructure/terraform/environments/production` compose VPC, RDS, and ECS services with outputs for ALB and database endpoints.
- **Ansible automation:** `infrastructure/ansible` inventory, group vars, and roles for hardening hosts, deploying the API/console via Compose, and pushing the OTel collector config.
- **Orchestration service:** `backend/app/routers/orchestration.py` with coverage in `backend/tests/test_orchestration.py`.
- **React console:** `frontend/src/pages/OrchestrationConsole.tsx` plus Navbar wiring to expose orchestration telemetry in the UI.
- **Container & cluster manifests:** `deployments/docker-compose.platform.yml` for local stacks and `deployments/k8s/platform.yaml` for Kubernetes rollout.
- **CI/CD pipeline:** `.github/workflows/platform-delivery.yml` validating Terraform, Ansible, backend API tests, and a console build.
- **Observability:** `observability/otel-collector.yaml`, `observability/grafana-dashboard.json`, and Grafana provisioning under `deployments/grafana-provisioning`.
- **Runbook & diagram:** `docs/orchestration-runbook.md` and `docs/diagrams/platform-orchestration.md` outline operations and data flow.
