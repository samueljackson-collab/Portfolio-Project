# Project 2: Database Migration Platform

Change data capture service enabling zero-downtime migrations between PostgreSQL clusters.

## Highlights
- Debezium connector configurations stored under `config/`.
- Python orchestrator coordinates cutover, validation, and rollback steps (`src/migration_orchestrator.py`).

## Phase 1 Architecture Diagram

Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

- **Context**: Migrations rely on Debezium CDC to stream changes into an orchestrator that coordinates AWS DMS tasks, validation, and rollback logic before promoting traffic.
- **Decision**: Separate source, control plane, and target cloud trust zones so CDC traffic, orchestration commands, and target writes are observable and rate-limited independently.
- **Consequences**: Cutovers are auditable with CloudWatch metrics from both the orchestrator and DMS, and rollback signals remain contained within the control plane. Keep the [Mermaid source](assets/diagrams/architecture.mmd) synchronized with the exported PNG.
