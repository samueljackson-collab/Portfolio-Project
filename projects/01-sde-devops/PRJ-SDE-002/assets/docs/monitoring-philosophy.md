# Monitoring Philosophy (USE + RED)

This stack applies the **USE** and **RED** methodologies to keep signals aligned to resource health and user experience while remaining noise-aware.

## USE (Utilization, Saturation, Errors)
- **Utilization:** Track how busy each resource is (CPU, memory, disk, network) with per-instance and fleet rollups.
- **Saturation:** Measure queued work and contention (run-queue length, disk I/O wait, TCP retransmits) to catch pressure before failure.
- **Errors:** Surface systemic faults (filesystem errors, exporter scrape failures, backup job non-zero exits) with explicit severities.

### USE Implementation Map
- **Prometheus** collects node-level metrics with 15s scrape intervals and 30s rule evaluations.
- **Recording rules** pre-aggregate CPU, memory, disk, and network ratios to cut dashboard latency.
- **Alert rules** distinguish critical saturation (95%+) from early-warning (80-90%) to minimize alert fatigue.

## RED (Rate, Errors, Duration)
- **Rate:** Request throughput and log ingest volume are sampled to spot unexpected traffic shifts.
- **Errors:** HTTP 5xx, gRPC failures, and log-derived error counts drive service reliability alerts.
- **Duration:** Response time percentiles (p50/p95/p99) power SLO tracking and regression detection.

### RED Implementation Map
- **Blackbox probes** track external availability for key URLs (staging and production).
- **Application dashboards** chart request rate vs. error rate to surface outliers.
- **Alertmanager routes** map RED-derived alerts to runbooks with explicit acknowledgement targets.

## Guiding Principles
1. **Actionable by default:** Every alert links to a runbook entry with first-response steps.
2. **Dashboards support decisions:** Visuals pair saturation with dependency health (e.g., CPU vs. queue depth) to prevent single-signal bias.
3. **Backups are part of observability:** PBS job status and retention drift are surfaced like any other SLI to keep recovery guarantees visible.
4. **Sanitized evidence:** All shared artifacts remove sensitive hostnames, IP addresses, and credentials; any value that looks real is a placeholder.
