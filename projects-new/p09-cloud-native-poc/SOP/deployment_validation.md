# P09 Cloud-Native POC — Day-2 Deployment Validation SOP

This SOP mirrors the structure of the P07/P08/P10 operational packs and focuses on day-2 tasks for the FastAPI-based cloud-native proof-of-concept. It defines pre-deployment controls, deployment-time validation, post-deployment checks, and rollback actions to maintain application availability and data integrity.

## Scope & Preconditions
- Applies to production and staging deployments of the FastAPI container, SQLite database, and supporting Docker runtime.
- Requires a scheduled change ticket, approved maintenance window, and on-call engineering + QA coverage.
- Confirm latest backups of `data/app.db` are available and restorable (see rollback steps).
- All changes must align with SLOs in the P09 runbook (availability 99.5%, p95 latency < 200ms, error rate < 1%).

## Pre-Deployment Checklist
- **Artifact readiness:**
  - Container image built from `main` and scanned for critical vulnerabilities.
  - Image tag recorded in change ticket and stored in the registry.
- **Configuration & secrets:**
  - Validate `.env`/runtime environment variables (`APP_ENV`, `DATABASE_URL`, logging level) match target environment.
  - Rotate secrets if older than 90 days and update any Docker secrets/variables accordingly.
- **Database safety:**
  - Capture a hot backup of `data/app.db` and upload to secure storage.
  - Dry-run pending migrations: `alembic upgrade head --sql > /tmp/p09_migrations.sql` (if Alembic is enabled).
- **Capacity & health baselines:**
  - Record current container stats: `docker stats cloud-native-poc --no-stream`.
  - Record baseline health: `curl -f http://localhost:8000/health && curl -f http://localhost:8000/ready`.
- **Observability hooks:**
  - Ensure log shipping/metrics exporters are running; confirm alert routes are in "maintenance" mode for the window.
- **Back-out readiness:**
  - Verify prior stable image tag (e.g., `p09-api:<last-good>`) is present locally or in registry.
  - Confirm rollback owners (platform engineer + QA) are reachable during the window.

## Deployment Validation (During Change)
- **Deploy or restart container:**
  ```bash
  docker pull <registry>/p09-api:<new-tag>
  docker stop cloud-native-poc || true
  docker run -d --rm --name cloud-native-poc \
    -p 8000:8000 \
    --env-file .env \
    <registry>/p09-api:<new-tag>
  ```
- **Immediate health checks (T+5 minutes):**
  - `curl -f http://localhost:8000/health` returns `{"status":"healthy"}`.
  - `curl -f http://localhost:8000/ready` returns `database: connected`.
  - `docker inspect cloud-native-poc | jq '.[0].State.Health.Status'` shows `healthy`.
- **Functional smoke tests:**
  - Create/read item cycle:
    ```bash
    ITEM_ID=$(curl -sf -X POST http://localhost:8000/api/items -H 'Content-Type: application/json' -d '{"name":"probe","price":1.99}' | jq -r '.id')
    curl -sf http://localhost:8000/api/items/$ITEM_ID
    ```
  - Verify OpenAPI spec is reachable: `curl -sf http://localhost:8000/openapi.json | head -n 5`.
- **Performance spot-check:**
  - `curl -w "time_total: %{time_total}s\n" -o /dev/null -s http://localhost:8000/api/items` should be < 0.2s (p95 target).
- **Log & metric verification:**
  - Tail structured logs for errors: `docker logs --tail 50 cloud-native-poc | grep -i error && false || true`.
  - If Prometheus enabled, validate `/metrics` endpoint returns HTTP 200.

## Post-Deployment Checks (Stabilization)
- **Extended monitoring (T+30 minutes):**
  - Confirm error rate < 1% and no restart loops: `docker inspect cloud-native-poc | jq '.[0].RestartCount'`.
  - Review container stats for sustained CPU < 70% and memory < 80%.
- **Database integrity:**
  - Run `sqlite3 data/app.db "PRAGMA integrity_check;"`.
  - Validate row counts match pre-deploy baseline within expected deltas: `sqlite3 data/app.db "SELECT COUNT(*) FROM items;"`.
- **Endpoint regression spot-checks:**
  - Run targeted regression suite if available: `pytest tests/api/test_items.py -q`.
  - Manually verify critical endpoints: `/health`, `/ready`, `/docs`, `/api/items` (list + create).
- **Security & configuration validation:**
  - Confirm TLS termination (if fronted by reverse proxy) still presents valid cert chain.
  - Verify logging level set to `INFO` (not `DEBUG`) in container env.
- **Documentation & change record:**
  - Update change ticket with deployed tag, validation results, and any deviations.

## Rollback Decision Criteria
- Health checks failing for > 5 minutes after deploy or restart count > 3 in 10 minutes.
- Error rate > 5% or p95 latency > 1s sustained for 10 minutes.
- Database integrity check fails or migrations introduce schema regression.
- Any P0/P1 incident triggered during or immediately after deployment window.

## Rollback Steps
1. **Stop current container:** `docker stop cloud-native-poc`.
2. **Restore last-known-good image:**
   ```bash
   docker pull <registry>/p09-api:<last-good>
   docker run -d --rm --name cloud-native-poc \
     -p 8000:8000 \
     --env-file .env \
     <registry>/p09-api:<last-good>
   ```
3. **Restore database (if schema/data corrupted):**
   ```bash
   docker stop cloud-native-poc
   cp /backups/app-db/<timestamp>/app.db data/app.db
   docker start cloud-native-poc
   ```
   - If migrations were applied, execute `alembic downgrade -1` before restoring backup (when Alembic is enabled).
4. **Validate rollback:** rerun health, readiness, and smoke tests from Deployment Validation section.
5. **Communicate:** Notify stakeholders of rollback, document root cause, and leave alerts in active mode.

## Communication & Ownership
- **Roles:** Platform/DevOps lead (execution + rollback), QA lead (validation), Service owner (sign-off).
- **Channels:** Deployment bridge, incident channel for any P1/P0 events, and change ticket for final notes.
- **Postmortem:** Required for any rollback or SLA breach; file within 48 hours with contributing factors and preventive actions.

## References
- P09 Runbook: `projects/p09-cloud-native-poc/RUNBOOK.md` for SLOs, alert queries, and operational baselines.
- Related packs: P07 roaming simulation, P08 API testing, P10 multi-region architecture runbooks for alerting and validation patterns.
