# Metrics & Observability Playbook

## Service Level Objectives & Error Budgets
| Domain | SLO | Measurement | Alert Threshold |
| --- | --- | --- | --- |
| Availability | 99.9% monthly for ALB + ECS service | Success rate (1-5xx) from ALB logs | Burn rate 2x over 1h or 4x over 5m |
| Latency | p95 < 250ms (read), p95 < 400ms (write) | ALB TargetResponseTime | p95 above target for 10m |
| Reliability | RDS replication lag < 100ms; CPU < 75% | RDS metrics | Lag > 1s for 5m or CPU > 80% for 10m |
| Cost Guardrails | ±10% of forecasted monthly | Infracost/usage dashboards | Variance >10% week-over-week |

## Key Metrics
- **ALB:** `HTTPCode_ELB_5XX`, `TargetResponseTime`, `RequestCount`, `RejectedConnectionCount`, WAF block rate.
- **ECS:** `CPUUtilization`, `MemoryUtilization`, `RunningTaskCount`, `ServiceUnavailable`, deployment failure events.
- **RDS:** `CPUUtilization`, `FreeableMemory`, `FreeStorageSpace`, `DatabaseConnections`, `TransactionLogsDiskUsage`, replication lag.
- **Application:** RED/USE metrics; tenant onboarding throughput; background job backlog depth.
- **Security:** WAF blocked requests, VPC Flow Log anomalies, IAM auth failures, secret rotation age.

## Logging
- **Structure:** JSON logs with `trace_id`, `span_id`, `user_id`, `request_path`, `duration_ms`, `status_code`, `env`.
- **Routing:** ECS tasks ship to CloudWatch Logs with per-env retention; ALB access logs, VPC Flow Logs, and audit events to S3 with lifecycle rules and bucket policies preventing deletion.
- **Correlation:** Propagate `traceparent` headers; OpenTelemetry auto-instrumentation for HTTP, DB, and queues.

## Dashboards & Alerts
- **Dashboards:** CloudWatch per env with ALB/ECS/RDS widgets, business KPIs, and log insights queries pinned with runbook links.
- **Alerts:**
  - ALB 5xx > 1% for 5 minutes → Page on-call; reference `OPERATIONS-PACKAGE.md`.
  - ECS CPU > 80% for 10 minutes or task restarts > 3 → Notify and auto-scale; create ticket if persistent.
  - RDS free storage < 15% or replication lag > 5s → Critical alert; validate backups.
  - Error budget burn > 70% → Change freeze recommendation and retro.
- **Escalation:** On-call → platform lead → incident commander within 30 minutes; security pager for auth anomalies.

## Tracing
- Enable OpenTelemetry SDK in services; export to X-Ray/Jaeger endpoint.
- Sample rate 5–10% in prod (adaptive based on traffic); 50–100% in lower environments for debugging.
- Key spans: DB queries, external API calls, queue operations, cache hits/misses, secrets retrieval.

## Synthetic Monitoring
- Canary checks hitting `/healthz` and representative CRUD flows every 5 minutes from multiple regions.
- Track availability by env; auto-create incident if two or more regions fail simultaneously.

## Run & Tune
- Weekly dashboard review with App + SRE + Security; adjust thresholds post-incident.
- Retention: logs 30–90 days (env-dependent); metrics 15 months via CloudWatch or Prometheus remote write.
- Backfill missing metrics with synthetic tests; ensure alarms link to runbooks and owners.
