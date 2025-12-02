# Project 2: Database Migration Platform

Change data capture service enabling zero-downtime migrations between PostgreSQL clusters.

## Highlights
- Debezium connector configurations stored under `config/`.
- Python orchestrator coordinates cutover, validation, and rollback steps (`src/migration_orchestrator.py`).

## Architecture Diagram

- ![Database migration architecture](assets/diagrams/architecture.svg)
- [Mermaid source](assets/diagrams/architecture.mmd)

**ADR Note:** Debezium/Kafka and AWS DMS run inside a dedicated migration control plane, with the orchestrator owning cutover, rollback, and CloudWatch/SNS signaling while isolating source and target PostgreSQL trust boundaries.
