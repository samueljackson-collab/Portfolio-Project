# Full-Scope Red Team Operation Simulator

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Simulate a 90-day advanced persistent threat (APT) campaign with day-by-day logging, detection tracking, and a companion React dashboard. This project is intentionally educational and **not** a real C2 framework.

## Highlights
- FastAPI backend with `Operation` and `OperationEvent` models for timeline tracking.
- Simulation endpoint that generates stealthy events with probabilistic detection based on a configurable `stealth_factor`.
- Operation status updates capture undetected streaks and the first time defenders detect activity.
- React UI renders covert vs. detected events, dashboard metrics, and quick-create workflows.

## File Tree
```
backend/app/routers/red_team.py
backend/app/services/security_simulations.py
frontend/src/pages/SecuritySimulators.tsx
frontend/src/components/security/SimulationBlocks.tsx
projects/full-scope-red-team/README.md
```

## API Primer
- `POST /red-team/operations` (auth) — create an operation with an objective and stealth factor.
- `POST /red-team/operations/{id}/simulate-next-day` (auth) — auto-generate the next day of activity with random detection.
- `POST /red-team/operations/{id}/events` (auth) — record manual events (validation enforces a 90-day window).
- `GET /red-team/operations/{id}/timeline` — filter by detection state or category for visualization.
- `POST /red-team/operations/{id}/mark-detected` (auth) — force a detection state without adding a new event.

### Detection & Status Logic
- Detection probability = `max(0.05, 1 - stealth_factor) + noise_bonus` where `noise_bonus` comes from event confidence.
- Each new event updates `days_elapsed`, undetected streak, and `first_detection_at` when applicable.
- Campaign length is capped at 90 days to mirror the requested APT window.

### Example Multi-Day Flow
1. `POST /red-team/operations` with `stealth_factor=0.8` to start the campaign.
2. `POST /red-team/operations/{id}/simulate-next-day?seed=3` to generate day 1.
3. Repeat simulation to grow the timeline, then add a noisy manual event to observe detection and streak resets.
4. Visualize in the React Security Simulators page (`/security-simulators`).

## Running the Simulator
- **Local**: `cd backend && uvicorn app.main:app --reload`; `cd frontend && npm install && npm run dev`.
- **Docker Compose**: reuse `backend/docker-compose.yml` to start Postgres + API, then run the Vite dev server separately.
- Sanity: `curl http://localhost:8000/health` and `npm run test` for the UI widgets.

## Detection Randomness Assumptions
- Events use a seeded RNG for tests; providing `seed` keeps UI demos reproducible.
- Higher stealth reduces base detection odds; noisier actions add a small bonus to defender detection.

## Blue-Team Countermeasure Notes
- The timeline highlights detected actions so blue teams can model alerting coverage.
- Operation status flips to `detected` on the first caught event, resetting the undetected streak for reporting.
