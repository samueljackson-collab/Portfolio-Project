# Metrics & Observability Playbook

## Service Level Objectives
- **Availability:** 99.9% monthly for ALB + ECS service; error budget burn alert at 40% and 70%.
- **Latency:** p95 < 250ms for read paths; p95 < 400ms for write paths.
- **Reliability:** RDS replication lag < 100ms; CPU < 75% sustained; connection saturation < 80%.

## Key Metrics
- **ALB:** `HTTPCode_ELB_5XX`, `TargetResponseTime`, `RequestCount`, `RejectedConnectionCount`.
- **ECS:** `CPUUtilization`, `MemoryUtilization`, `RunningTaskCount`, `DeploymentFailure` events.
- **RDS:** `CPUUtilization`, `FreeableMemory`, `FreeStorageSpace`, `DatabaseConnections`, `TransactionLogsDiskUsage`.
- **Application:** Request rate, error rate, duration (RED), custom business KPIs (e.g., tenant onboarding/sec).
- **Security:** WAF blocked requests, VPC Flow Log anomaly counts, IAM auth failures.

## Logging
- **Structure:** JSON logs with `trace_id`, `span_id`, `user_id`, `request_path`, `duration_ms`, `status_code`.
- **Routing:** ECS tasks ship to CloudWatch Logs with retention by env; ALB access logs and VPC Flow Logs to S3 with lifecycle rules.
- **Correlation:** Propagate `traceparent` headers; integrate with X-Ray or OpenTelemetry collector sidecar.

## Dashboards & Alerts
- **Dashboards:** CloudWatch dashboards per env with ALB/ECS/RDS widgets, log query widgets, and business KPI charts.
- **Alerts:**
  - ALB 5xx > 1% for 5 minutes → Page on-call.
  - ECS CPU > 80% for 10 minutes or task restarts > 3 → Notify and auto-scale.
  - RDS free storage < 15% or replication lag > 5s → Critical alert.
  - Error budget burn > 70% → Change freeze recommendation.
- **Escalation:** On-call → platform lead → incident commander within 30 minutes.

## Tracing
- Enable OpenTelemetry SDK in services; export to X-Ray/Jaeger endpoint.
- Sample rate 5–10% in prod; 50–100% in lower environments for debugging.
- Key spans: DB queries, external API calls, queue operations, cache hits/misses.

## Run & Tune
- Review dashboard weekly; tune thresholds after incident postmortems.
- Keep retention: logs 30–90 days (env-dependent); metrics 15 months via CloudWatch metrics or Prometheus remote write.
- Backfill missing metrics with synthetic canaries hitting `/healthz` and representative CRUD flows.
