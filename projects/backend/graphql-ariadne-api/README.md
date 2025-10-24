# GraphQL API with Ariadne

## Overview
GraphQL service providing flexible querying for analytics and reporting use cases. Built with Ariadne, SQLAlchemy, and async PostgreSQL connectors.

## Features
- Schema-first design with SDL files under `schema/`.
- Data loaders to batch requests and reduce N+1 queries.
- Subscription support via WebSockets for real-time updates.
- Federation-ready resolvers to integrate with future supergraph.

## Setup
1. Install dependencies: `poetry install`.
2. Configure `.env` with database URL and service secrets.
3. Run migrations: `alembic upgrade head` (shared with FastAPI service or read replica).
4. Start server: `poetry run uvicorn app.main:app --reload`.
5. Tests: `pytest`, GraphQL contract tests via `pytest-snapshot` and `schemathesis` for schema validation.

## Observability & Security
- GraphQL depth/complexity limits to prevent abuse.
- Persisted queries stored in Redis; whitelist enforced at gateway.
- Metrics exported via Apollo integration or OpenTelemetry.

## Operations
- Deployable via Helm chart (shared templates).
- Runbook includes resolver performance tuning and caching strategies.

