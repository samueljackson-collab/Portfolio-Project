# Python FastAPI Backend API

## Overview
A production-ready REST API implementing task management, user profiles, and integration points for downstream services. Built with FastAPI, SQLModel, and async PostgreSQL drivers to provide high throughput and type-safe endpoints.

## Architecture
- **Application Layer:** FastAPI with modular routers for tasks, users, analytics, and health endpoints.
- **Persistence:** PostgreSQL (via `iac/rds-postgresql-infra`) with Alembic migrations and read replicas for reporting.
- **Caching:** Redis or Elasticache for hot data and rate limiting.
- **Messaging:** Publishes domain events to Kafka (`events.tasks`) consumed by data pipelines.
- **Security:** OAuth2 with JWT, scopes enforced via dependency injection, API keys for service accounts.

## Setup
1. Create Python environment: `poetry install`.
2. Copy `.env.example` to `.env` with database DSN, Redis URL, and JWT secrets (pulled via AWS Secrets Manager in production).
3. Run database migrations: `alembic upgrade head`.
4. Start API: `uvicorn app.main:app --reload`.
5. Execute tests: `poetry run pytest`.

## Quality & Reliability
- Type hints validated by `mypy`.
- Contract tests maintained for interactions with React app and serverless API.
- Pydantic models include JSON schema exported for documentation.
- OpenAPI spec published to S3 and versioned.

## Observability & Ops
- Structured logging via `structlog` with trace/span correlation.
- Metrics exported via Prometheus `/metrics` endpoint.
- Distributed tracing integrated with OpenTelemetry instrumentation library.
- Runbook outlines scaling (HPA), blue/green deployments through Argo Rollouts, and rollback procedures.

## Security
- Input validation, rate limiting, and WAF integration for public endpoints.
- Secrets pulled at runtime via AWS Parameter Store (with local fallback in `.env`).
- Regular dependency scanning and container image hardening using multi-stage Dockerfile (`projects/devops/dockerfile-fastapi`).

