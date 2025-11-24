# Master Artifacts

Authoritative pointers to the code, infrastructure, and operational assets used by the roaming simulation platform.

## Infrastructure-as-Code
- **Dual-region Terraform plan**: `infrastructure/terraform/dual-region/` provisions paired VPCs, subnets, ALBs, and security groups with primary/secondary regions and OTLP ingress controls.
- **Ansible rollout**: `infrastructure/ansible/dual-region/` inventory and `roles/roaming_api` ship the FastAPI container with OTLP wiring across both regions.

## Application Services
- **FastAPI roaming endpoints**: `backend/app/routers/roaming.py` with session store at `backend/app/services/roaming.py`; schemas live in `backend/app/schemas.py` and tests in `backend/tests/test_roaming.py`.
- **Operator console**: React console in `frontend/src/pages/RoamingConsole.tsx` with UI widgets under `frontend/src/components/roaming/` and API client in `frontend/src/api/roaming.ts`.
- **Docker delivery**: Hardened build recipes in `backend/Dockerfile` and `frontend/Dockerfile` (nginx config at `frontend/nginx.conf`).

## Observability & Operations
- **OTel collector pipeline**: `operations/observability/otel/collector.yaml` scrapes FastAPI/OTLP and forwards to remote backends.
- **Dashboards**: Operator dashboard definition at `operations/observability/dashboards/roaming-overview.json`.
- **Runbooks**: Scenario operations runbook at `projects/p07-roaming-simulation/RUNBOOK.md` aligns with the API and console flows.

## Supply Chain & CI/CD
- **SBOM generation and signing**: `tools/supply-chain/generate-and-sign-sbom.sh` with automated invocation via `.github/workflows/supply-chain.yml`.
- **GitHub Actions**: Workflow above also builds the backend image, runs FastAPI roaming tests, and archives signed SBOM artifacts.

