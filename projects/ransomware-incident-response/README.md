# Ransomware Incident Response & Recovery Simulator

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Model the full ransomware lifecycle with deterministic sequencing, JWT-protected mutations, and a React dashboard section for analysts.

## Highlights
- FastAPI `Incident` and `IncidentEvent` models capture Detection → Containment → Eradication → Recovery → Lessons Learned.
- `POST /incidents/{id}/simulate` appends ordered lifecycle events with generated timestamps.
- Ordering validation warns when analysts submit out-of-sequence events.
- Frontend timeline renders the lifecycle and refresh buttons to replay drills.

## File Tree
```
backend/app/routers/ransomware.py
backend/app/services/security_simulations.py
frontend/src/pages/SecuritySimulators.tsx
frontend/src/components/security/SimulationBlocks.tsx
projects/ransomware-incident-response/README.md
```

## API Quickstart
- `POST /incidents` (auth) — create an incident record.
- `POST /incidents/{id}/simulate` (auth) — generate the remaining lifecycle stages.
- `POST /incidents/{id}/events` (auth) — add a custom lifecycle event with ordering validation.
- `POST /incidents/{id}/resolve` (auth) — mark the drill as resolved.
- `GET /incidents/{id}/timeline` — review ordered events.

### Simulation & Validation
- Sequencing is state-machine style with 30-minute offsets between events.
- Invalid ordering returns a warning while preserving the timeline for retrospective analysis.

### Usage Walkthrough
1. Create an incident with `severity=critical`.
2. Call `/simulate` to generate the full lifecycle or add events manually (expect warnings on out-of-order submissions).
3. Track status changes and resolution timestamps in the UI timeline.

## Running Locally
- Backend: `cd backend && uvicorn app.main:app --reload`.
- Frontend: `cd frontend && npm install && npm run dev`; open `/security-simulators` to interact.
- Health check: `curl http://localhost:8000/health`.

## Access Control Notes
- JWT enforcement on all mutation routes mirrors real-world RBAC expectations.
- Automation endpoints are deliberately deterministic for CI and tabletop repeatability.
