# Enterprise EDR Platform Simulation

Simulate endpoint registration, policy toggling, and deployment coverage with FastAPI and a React admin console.

## Highlights
- Models: `EndpointAsset`, `EndpointPolicy`, and `EndpointAlert` with JWT-protected mutation routes.
- Auto-alerting for outdated agents on registration/check-in via helper heuristics.
- Coverage summary endpoint powers the dashboard (online count, outdated agents, policy totals).

## File Tree
```
backend/app/routers/edr.py
backend/app/services/security_simulations.py
frontend/src/pages/SecuritySimulators.tsx
frontend/src/components/security/SimulationBlocks.tsx
projects/edr-platform/README.md
```

## API Overview
- `POST /edr/endpoints` (auth) — register an endpoint (may emit outdated-agent alert).
- `POST /edr/endpoints/{id}/checkin` (auth) — heartbeat plus optional agent upgrade.
- `GET /edr/deployment/summary` — deployment coverage metrics.
- `GET /edr/policies` & `PATCH /edr/policies/{id}` — list/toggle policies.
- `GET /edr/alerts` — review alerts raised during enrollment/check-ins.

## Deployment Simulation
- Outdated version heuristic compares semantic version parts against a baseline (`1.5.0`).
- Coverage = online endpoints / total endpoints, exposed as a simple percentage for tuning exercises.

## Usage
1. Register endpoints with varying agent versions to trigger alerts.
2. Toggle policies to simulate rollout stages.
3. Watch coverage and outdated counts update in the UI dashboard.

## Running & Validation
- Backend health: `/health`.
- Tests: `pytest` (backend) and `npm run test` (frontend components) for regression coverage.
- Local dev: `uvicorn app.main:app --reload` and `npm run dev`.
