# ADR-005: CloudWatch-Centric Observability with Tracing Hooks

- **Status:** Accepted
- **Date:** 2025-05-14

## Context
The platform requires unified visibility into application performance, infrastructure health, and security events without deploying additional heavy infrastructure. We need rapid onboarding and native integration with AWS services.

## Decision
- Use **Amazon CloudWatch** for metrics, logs, dashboards, and alarms as the primary observability plane.
- Ship logs from ALB, ECS tasks, and VPC Flow Logs to CloudWatch/S3 with structured JSON schema.
- Integrate **OpenTelemetry** in services with exporters to **AWS X-Ray** (or Jaeger in future) for distributed tracing.
- Define **SLOs** for availability and latency with error budget alerts and synthetic canaries.

## Consequences
- ✅ Minimal extra infrastructure; leverages managed AWS capabilities.
- ✅ Fast time-to-detect with unified metrics/logs and tracing correlations.
- ⚠️ Vendor lock-in for observability; migration would require re-instrumentation/export pipelines.
- ⚠️ Additional CloudWatch costs for high-volume logs; mitigate with retention policies and filters.
