# Master Artifacts

Authoritative locations for infrastructure as code, service endpoints, operator consoles, and observability assets.

## Infrastructure
- **Dual-region Terraform stack:** `infrastructure/terraform/dual-region-sim/` (providers, VPC/ECS modules, outputs)
- **Terraform modules:** `infrastructure/terraform/modules/` (shared VPC, ECS application, database)
- **Ansible orchestration:** `infrastructure/ansible/dual-region-sim.yml` with inventory `infrastructure/ansible/inventory.yml`

## Backend Services (FastAPI)
- **Application factory and router wiring:** `backend/app/main.py`
- **Roaming lifecycle schemas:** `backend/app/schemas.py`
- **Roaming domain logic:** `backend/app/services/roaming.py`
- **Roaming API endpoints:** `backend/app/routers/roaming.py`
- **API contract tests:** `backend/tests/test_roaming.py`

## Frontend Operator Console (React)
- **Roaming console page:** `frontend/src/pages/RoamingConsole.tsx`
- **Session table component:** `frontend/src/components/roaming/RoamingSessionTable.tsx`
- **Routing/Nav wiring:** `frontend/src/App.tsx`, `frontend/src/components/Navbar.tsx`

## Supply Chain & Deployment
- **Hardened backend image:** `backend/Dockerfile`
- **Hardened frontend image:** `frontend/Dockerfile`
- **SBOM generation and signing workflow:** `.github/workflows/supply-chain.yml`

## Observability
- **OpenTelemetry collector config:** `observability/otel/collector-dual-region.yaml`
- **Grafana dashboard JSON:** `observability/otel/grafana/roaming-dashboard.json`

## Runbooks & Reference Assets
- **Roaming operator runbook stub deployed by Ansible:** `/etc/roaming_runbook.txt` (generated via `infrastructure/ansible/dual-region-sim.yml`)
- **Health/metrics endpoints exposed via FastAPI:** `/health`, `/metrics`, `/roaming/sessions`
