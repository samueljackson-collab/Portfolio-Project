# Dashboard Rationale

This portfolio includes exportable Grafana dashboards that align with the monitoring philosophy.

## Infrastructure Overview
- **Goal:** Rapidly answer "is the platform healthy?" using USE signals.
- **Key Panels:** Host counts, CPU/memory/disk saturation, network throughput, scrape health, and storage latency.
- **Design Notes:** Stat panels for at-a-glance health, time-series for trends, and thresholds tuned to warning/critical levels that match alert rules.

## Application Reliability (RED)
- **Goal:** Track customer-facing latency and errors while correlating with dependencies.
- **Key Panels:** Request rate, success/error ratio, latency percentiles, queue depth, and downstream dependency success.
- **Design Notes:** Panels reuse recording rules to avoid Grafana-side heavy queries; templating enables per-service drill-down.

## Alerting & Backup Assurance
- **Goal:** Visualize current alerts, alert aging, and backup status in one view for on-call.
- **Key Panels:** Active alerts by severity, mean time to acknowledge, backup success ratio, retention compliance, and restore test outcomes.
- **Design Notes:** Uses Loki log counts for error spikes and Prometheus rules for PBS job health; links to runbooks for each alert.

## Sanitization Notes
- Dashboards use generic datasources (`prometheus`, `loki`) and placeholder host labels (`edge-node-01`, `api-gateway`) instead of real infrastructure identifiers.
- All example screenshots are generated from synthetic sample metrics so no production traffic is exposed.
