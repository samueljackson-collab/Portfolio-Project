# Monitoring & Alerting Philosophy (USE/RED)

This document explains the monitoring strategy used in PRJ-SDE-002, pairing the **USE** (Utilization, Saturation, Errors) method for infrastructure components with the **RED** (Rate, Errors, Duration) method for request-driven services.

## Guiding Principles
- **Simplicity first:** Default to a handful of golden signals per component; only add panels when they answer a recurring question.
- **Actionability:** Every alert maps to a runbook link and an expected response time.
- **Separation of concerns:** Metrics, logs, and traces remain isolated but are correlated through consistent labels (`project="PRJ-SDE-002"`, `service`, `instance`).
- **Sanitized by design:** Configs and screenshots remove customer data, tokens, and routable IPs.

## USE: Infrastructure
- **Utilization:** CPU, memory, and disk usage from Node Exporter and cAdvisor panels (`infrastructure-overview.json`).
- **Saturation:** Disk I/O wait, network saturation, and queue depth panels help catch headroom issues before errors appear.
- **Errors:** Filesystem errors, failed scrapes, and service restarts feed into the `Infrastructure Availability` panel and `HostDown` alert.

## RED: Services
- **Rate:** HTTP request volume, gRPC QPS, and job throughput appear in `application-metrics.json` and `alert-operations.json`.
- **Errors:** 4xx/5xx ratios and retry rates are routed to the `Error Budget` panel and `HighErrorRate` alert.
- **Duration:** p50/p95 latency heatmaps backstop SLO monitoring; budget burn alerts fire when sustained latency exceeds SLOs.

## Dashboard Rationale
- **Infrastructure Overview:** Immediate health via golden signals and exporter uptime; aligns to USE.
- **Application Metrics:** Request patterns, error ratios, and worker saturation; aligns to RED.
- **Alert Operations:** Combines alert volume, MTTA/MTTR, and silences to validate alert hygiene.
- **PBS Backups:** Tracks backup duration, throughput, dedup ratio, and retention horizon to ensure RPO/RTO.

## Alert Runbooks
- Alerts map to runbooks in `assets/runbooks/` with quick links embedded in Alertmanager templates.
- Each runbook contains: symptoms, validation commands, a decision tree, and rollback guidance.
- Critical alerts (`HostDown`, `BackupJobFailed`, `LogErrorRate`) page on-call; warnings generate tickets for follow-up.

## Backups & Recovery
- PBS job definitions are in `backups/pbs-job-plan.yaml`; retention validation is captured in `pbs-retention-report.md`.
- Backup verification uses `scripts/verify-pbs-backups.sh` to test restores in a sandbox.
- Grafana and Prometheus volumes are captured as part of the `observability-stack` job to maintain dashboards and TSDB continuity.

## Lessons Learned
- Align dashboards to questions operators actually ask; prune noisy panels monthly.
- Budget burn alerts outperformed raw error counts for catching partial outages.
- Stagger PBS jobs to avoid NFS saturation and to keep Prometheus I/O headroom stable.
- Always export dashboards and configs immediately after an incident while context is fresh.

## Sanitization Checklist
- [x] Webhooks and email addresses replaced with placeholders.
- [x] IPs/hostnames reduced to non-routable examples.
- [x] Screenshots rendered with demo data only.
- [x] Backups and job exports omit credentials and tokens.
