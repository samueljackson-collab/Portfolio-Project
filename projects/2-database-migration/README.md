# Project 2: Database Migration Platform

Change data capture service enabling zero-downtime migrations between PostgreSQL clusters.

## Highlights
- Debezium connector configurations stored under `config/`.
- Python orchestrator coordinates cutover, validation, and rollback steps (`src/migration_orchestrator.py`).
