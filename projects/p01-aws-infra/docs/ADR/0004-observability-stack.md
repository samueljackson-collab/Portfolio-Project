# ADR 0004 — Observability Stack

**Status**: Accepted
**Date**: 2024-11-10
**Deciders**: SRE Lead, Platform Observability Engineer

## Context
The platform needs consistent logging, metrics, and tracing to detect drift, performance regressions, and incidents across environments. Tooling must integrate with AWS-native services, support infrastructure-as-code deployment, and provide long-term retention for audit events. Observability should minimize vendor lock-in while enabling alert routing to PagerDuty and collaboration channels.

## Decision
Adopt an **AWS-native observability stack** complemented by lightweight open-source components:
- **CloudWatch Logs** for centralized log ingestion with subscription filters to **Kinesis Firehose → S3** for archival.
- **CloudWatch Metrics** with **AWS Distro for OpenTelemetry (ADOT)** collectors for application metrics.
- **X-Ray** for distributed tracing of service calls within the VPC.
- **CloudTrail** enabled across all accounts with organization-wide trail and 365-day retention in S3.
- Alerting via **CloudWatch Alarms → SNS → PagerDuty** and **Ops Slack** webhooks.

## Alternatives Considered
- **Datadog**: Rich features and unified UI but adds licensing costs and agent overhead; deferred until scale demands.
- **ELK/Opensearch self-managed**: Flexible querying but increases operational toil (scaling clusters, patching, storage tuning).
- **Prometheus + Grafana Cloud**: Strong metrics/tracing support but introduces multi-vendor management and cross-account networking complexity.

## Consequences

### Positive
- Rapid adoption with minimal new tooling; uses managed AWS services already approved for compliance.
- Unified alerting path to PagerDuty and Slack; no separate alerting stack to maintain.
- Long-term auditability via CloudTrail and S3 archives.

### Negative
- CloudWatch query experience is less user-friendly than dedicated observability vendors.
- X-Ray sampling may obscure low-volume traces unless tuned carefully.
- Kinesis/S3 archival adds incremental costs.

### Mitigation
- Provide ready-made CloudWatch Logs Insights queries in RUNBOOK.md for common investigations.
- Tune ADOT and X-Ray sampling per environment and document defaults.
- Set lifecycle policies on S3 archives and Kinesis delivery streams to manage storage spend.
