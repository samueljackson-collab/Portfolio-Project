# Runbooks — P09

## Runbook: Local Dev Stack
1. `cp .env.example .env` and set `DATABASE_URL=sqlite:///./data.db`.
2. `docker compose -f docker/compose.poc.yaml up --build`.
3. Verify `http://localhost:8000/healthz` returns 200.
4. Run `make test` inside container or host.

## Runbook: Database Migration
1. Update SQLModel models.
2. Generate migration script `alembic revision --autogenerate -m "desc"`.
3. Apply migration `alembic upgrade head` (ensure backup if Postgres).
4. Run integration tests targeting updated schema.

## Runbook: Worker Backlog Drain
1. Check queue depth via `/metrics` (`p09_queue_depth`).
2. Temporarily scale worker `kubectl scale deployment p09-worker --replicas=3`.
3. Monitor retries; scale back to 1 when `p09_queue_depth` steady.
