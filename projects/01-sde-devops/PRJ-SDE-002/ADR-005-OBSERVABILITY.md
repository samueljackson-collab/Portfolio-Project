# ADR-005: Observability Standards

## Status
Accepted

## Context
The platform itself must be observable and resilient. Ad hoc dashboards and alerts create noisy signals and slow incident response.

## Decision
- Define **golden signals** (latency, traffic, errors, saturation) per service and create standardized dashboards in Grafana using git versioning.
- Maintain **alert taxonomy** (sev0-sev3) with runbook links, inhibition rules, and on-call routing; implement automatic ticket creation via webhooks.
- Instrument pipelines and backup jobs with **SLOs** (availability, restore success rate, alert delivery time) and publish to a health dashboard.
- Enable **self-monitoring**: Prometheus and Loki exporters, Grafana health dashboards, Alertmanager status panel, PBS job success metrics.

## Consequences
- Pros: Consistent alert quality, faster MTTR/MTTA, audit-ready dashboards.
- Cons: Upfront dashboard curation and periodic rule tuning required.
- Follow-ups: Add synthetic probes for critical user journeys; track error budgets and automate release gates based on SLO burn rate.
