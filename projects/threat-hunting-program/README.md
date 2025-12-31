# Proactive Threat Hunting Program

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Capture hunt hypotheses, findings, and promoted detection rules with a simple FastAPI + React workflow.

## Highlights
- CRUD for hypotheses plus per-hypothesis findings via FastAPI.
- Promotion endpoint turns a finding into a draft detection rule for quick SIEM deployment.
- React board view surfaces hypotheses next to their rules for analyst hand-offs.

## File Tree
```
backend/app/routers/threat_hunting.py
backend/app/services/security_simulations.py
frontend/src/pages/SecuritySimulators.tsx
frontend/src/components/security/SimulationBlocks.tsx
projects/threat-hunting-program/README.md
```

## API Notes
- `POST /threat-hunting/hypotheses` (auth) — seed a new hunt idea.
- `POST /threat-hunting/hypotheses/{id}/findings` (auth) — log evidence with severity.
- `POST /threat-hunting/findings/{id}/promote` (auth) — create a `DetectionRule` tied to the finding.
- `GET /threat-hunting/detection-rules?status=Draft` — filter rules by lifecycle.

## Workflow Example
1. Create a hypothesis for suspicious PowerShell remoting.
2. Add a high-severity finding with encoded command details.
3. Promote to a detection rule to share with the detection engineering team.
4. Track promoted vs. open hypotheses in the UI board.

## Running & Validation
- Backend tests cover promotion and linkage; run `cd backend && pytest`.
- Frontend widgets validated via `npm run test` (renders findings and rules).
- Health check at `/health` remains available for probes.
