# Master Artifacts

Curated index of delivery-ready assets implemented in the repository.

## Infrastructure and GitOps
- **AWS multi-region Terraform stack:** `infrastructure/terraform/multi-region` provisions paired VPCs, replicated artifact buckets, DynamoDB global tables, and EKS control planes with environment overlays defined in `envs/`.  
- **GitOps overlays and Argo CD application:** `infrastructure/gitops/base` with regional overlays at `infrastructure/gitops/overlays/us-east-1` and `.../eu-west-1`, plus the Argo CD application manifest in `infrastructure/gitops/applications/multi-region-app.yaml` for automated reconciliation.

## Platform Services
- **Deployment ledger model and API:** `backend/app/models.py`, `backend/app/routers/deployments.py`, and `backend/app/services/deployment_service.py` expose authenticated CRUD and rollup endpoints for regional deployments.  
- **Database migration:** Alembic revision `backend/alembic/versions/20251115_1200_add_service_deployments.py` creates the `service_deployments` table.
- **Service tests:** `backend/tests/test_deployments.py` validates creation, listing, and dashboard aggregation paths.

## Frontend Operator Console
- **React operator console:** `frontend/src/pages/OperatorConsole.tsx` renders region health cards and release tables backed by `operationsService` in `frontend/src/api/services.ts` with typed payloads in `frontend/src/api/types.ts`. Routes are wired in `frontend/src/App.tsx` and exports in `frontend/src/pages/index.ts`.

## Delivery and Runtime Hardening
- **Hardened container builds:** Updated multi-stage Dockerfiles for API (`backend/Dockerfile`) and frontend (`frontend/Dockerfile`) run as non-root with health checks.  
- **CI pipeline:** `.github/workflows/platform-delivery.yml` executes backend tests with an ephemeral database, builds the React bundle, and produces Docker images.

## Observability and Runbooks
- **Dashboards and alerts:** Grafana board at `operations/observability/grafana-multi-region.json` and Prometheus alert rules in `operations/observability/prometheus-alerts.yaml` cover health and replica drift.  
- **Operations runbook:** `operations/observability/runbook.md` documents diagnosis and remediation flows for regional outages and rollout failures.
