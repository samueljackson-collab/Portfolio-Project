# P09 · Full-Stack Cloud Application — Incident Playbook

## P1 — API Outage (All Customers Impacted)
1. PagerDuty triggers `P09-API` service; join incident bridge.
2. Validate `/health` endpoint failure and review recent deploys (GitHub Actions, Argo CD history).
3. Initiate rollback using `argocd app rollback p09-api <previous-revision>`.
4. Confirm recovery via `scripts/test/smoke-tests.sh` and Grafana dashboard.
5. Communicate incident timeline on status page and Slack `#p09-incident`.

## P1 — Database Connectivity Loss
1. Check RDS status; if Multi-AZ failover underway, monitor completion.
2. If failover stalled, execute `aws rds reboot-db-instance --force-failover` targeting `portfolio-db`.
3. Once healthy, run database smoke test: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM example_health_events;"`.
4. Validate API `/health/db` endpoint; if still failing, trigger application recycle via Argo CD.

## P2 — Elevated Error Rate (5xx > 5%)
1. Inspect `/metrics` for spikes in `database_visits` and Redis counters.
2. Correlate with recent code changes; if necessary, enable feature flag rollback via configuration service.
3. Scale API deployment temporarily using `kubectl scale deployment p09-api --replicas=6`.
4. Monitor Alertmanager notifications until error rate returns below threshold for 30 minutes.

## P2 — Redis Evictions Detected
1. Run `redis-cli info memory` to confirm `evicted_keys` increasing.
2. Flush non-critical keys: `redis-cli --scan --pattern 'cache:*' | xargs redis-cli del`.
3. Increase maxmemory via parameter store change or scale Redis cluster.
4. Update observability dashboard with incident annotation.

## P3 — Frontend Deployment Failure
1. Check GitHub Actions artifact `frontend-build` for compilation errors.
2. Re-run build locally `npm run build` to reproduce; fix lint/test failures.
3. Redeploy via `npm run deploy` (CloudFront invalidation) after fix merges.
4. Notify marketing/support once resolved.

## Communication Templates
- **Initial:** "We are investigating an issue affecting the analytics portal. Next update in 15 minutes."
- **Mitigation:** "Mitigation underway (rollback to previous release). Monitoring recovery metrics."
- **Resolved:** "Service restored at <time>. Cause: <summary>. Follow-up actions captured in incident ticket."

Document each incident in `documentation/security/incidents/` with timeline, impact, and remediation steps.
