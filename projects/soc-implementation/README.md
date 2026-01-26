# Security Operations Center (SOC) Portal

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


A lightweight SOC experience with alert intake, case management, playbooks, and deterministic alert generation for demos.

## Highlights
- FastAPI `SocAlert`, `SocCase`, and `SocPlaybook` models with JWT-protected mutations.
- Automation endpoint to generate fake alerts (brute force, malware, impossible travel).
- React dashboard section with severity coloring, status indicators, and navigation into alerts/cases.

## File Tree
```
backend/app/routers/soc.py
backend/app/services/security_simulations.py
frontend/src/pages/SecuritySimulators.tsx
frontend/src/components/security/SimulationBlocks.tsx
projects/soc-implementation/README.md
```

## API Overview
- `POST /soc/alerts` (auth) — create or update alerts.
- `GET /soc/alerts` — list with optional filters.
- `POST /soc/alerts/generate` (auth) — seed the system with fake alerts.
- `POST /soc/cases` (auth) — create a case and attach alerts.
- `GET /soc/playbooks` — list curated playbooks to attach to cases.

## Fake Alert Generation
- Generates three realistic alerts to exercise severity styling and case assignment workflows.
- Defaults to the included playbooks (`Credential Theft Containment`, `Webshell Eradication`).

## Usage
1. Generate alerts, then create a case with selected alert IDs.
2. Update alert status or severity as investigations progress.
3. Review playbook steps in the UI to guide response.

## Running
- Backend: `uvicorn app.main:app --reload` from `backend/`.
- Frontend: `npm run dev` from `frontend/`, then open `/security-simulators`.
- CI-friendly: `npm run test` to exercise UI components; `pytest` for API tests.
