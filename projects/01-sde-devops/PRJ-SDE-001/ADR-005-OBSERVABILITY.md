# ADR-005: Observability & Monitoring

## Context
To maintain reliability and meet SLOs, we need consistent metrics, logs, and traces with actionable alerts and clear ownership.

## Decision
- Collect **metrics** from ALB, ECS, and RDS; expose application RED/USE metrics via OpenTelemetry exporters.
- Standardize **structured JSON logging** with correlation IDs; ship ECS task logs to CloudWatch with retention policies; ALB/VPC logs to S3.
- Implement **tracing** using OpenTelemetry SDKs with X-Ray/Jaeger backend; propagate `traceparent` headers through services.
- Build **CloudWatch dashboards and alarms** per environment aligned to SLOs; alerts routed to PagerDuty/Slack with runbook links.
- Add **synthetic canaries** for `/healthz` and critical user journeys to detect regressions early.

## Consequences
- Improved incident detection and triage; requires disciplined instrumentation in application services.
- Additional cost for telemetry storage; mitigated by retention policies and sampling rates.
- Dashboards and alarms become release gates, increasing confidence but requiring maintenance.

## Status
Accepted
