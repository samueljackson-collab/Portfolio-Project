# P09 · Full-Stack Cloud Application — Operations Runbook

> **Audience:** Product engineers and SREs operating the customer analytics SaaS.

---
## 1. Service Overview
- **Frontend:** React SPA hosted on CloudFront (local development served via `docker-compose` frontend container).
- **Backend:** FastAPI service (`examples/fullstack/api`) backed by PostgreSQL and Redis.
- **Background Jobs:** Celery workers (planned) triggered via Redis streams.
- **Monitoring:** Prometheus scraping `/metrics`; Grafana dashboard `P09-Operations`.

---
## 2. Daily Tasks
| Time (UTC) | Task | Responsible | Tooling |
| --- | --- | --- | --- |
| 02:00 | Verify API health endpoints (`/health`, `/health/db`, `/health/redis`) | On-call SRE | `scripts/test/smoke-tests.sh` |
| 08:00 | Review error budget burn-down chart | Product SRE | Grafana |
| 12:00 | Check Redis memory usage (< 70% threshold) | Backend Engineer | `redis-cli info memory` |
| 16:00 | Confirm nightly backup of PostgreSQL succeeded | DBA | AWS Backup report |
| 20:00 | Inspect deployment pipeline results for regressions | Dev Lead | GitHub Actions |

---
## 3. Deployment Steps
1. Create feature branch and open PR with tests (`npm test`, `pytest`).
2. Merge triggers GitHub Actions: lint → test → build container images → push to registry.
3. Promote to staging via Argo CD ApplicationSet (`projects/3-kubernetes-ci-cd/argo-cd/applicationset.yaml`).
4. Run `scripts/test/smoke-tests.sh https://staging.app.example.com https://staging.api.example.com`.
5. Execute load test snapshot (`scripts/test/performance-tests.sh https://staging.api.example.com 30`).
6. Obtain change approval, then promote to production via Argo CD.

---
## 4. Backup & Restore
- **Database:** Automated snapshots daily; manual run using `scripts/backup/full-backup.sh`.
- **Redis:** AOF enabled (see `docker-compose.yml` command). Export snapshot weekly for audit.
- **File Storage:** S3 bucket versioning enabled; restore via AWS CLI `aws s3 cp --recursive`.

Restore Procedure:
1. Provision temporary PostgreSQL instance.
2. Apply latest snapshot, then replay write-ahead logs.
3. Point staging environment to restored instance and validate application functionality.
4. Promote fix to production only after validation sign-off.

---
## 5. Observability
- `/metrics` endpoint exposes visit counters for dashboards.
- Prometheus scrape configured in `monitoring/prometheus/prometheus.yml`.
- Alert rules defined in `monitoring/prometheus/alert-rules.yaml` for latency, errors, and container restarts.
- Logs shipped to Loki via `docker-compose` (developers) and Fluent Bit (production).

---
## 6. Access Management
- Engineers authenticate via AWS SSO `P09-Developer` group.
- Production database access restricted to DBA group; temporary credentials issued via Vault.
- API secrets stored in AWS Secrets Manager; rotate quarterly.

---
## 7. Change Communication
- Announce planned production deployments in `#release-updates` with impact summary.
- For incidents, follow playbook communication templates and update status page (`status.example.com`).

---
## 8. KPI Targets
- **Availability:** 99.9% monthly.
- **p95 Latency:** ≤ 200 ms.
- **Error Rate:** ≤ 1% 5xx per rolling hour.
- **Customer-impacting incidents:** ≤ 2 per quarter.

KPIs tracked in Grafana; failure to meet thresholds triggers a post-incident review.
