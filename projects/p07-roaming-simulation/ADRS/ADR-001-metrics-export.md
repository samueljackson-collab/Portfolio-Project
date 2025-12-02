# ADR-001: Metrics Export Path

## Status
Accepted

## Context
The roaming simulator initially produced only log files. Observability requirements now demand Prometheus metrics for attach success, latency, and billing events.

## Decision
- Embed a Prometheus exporter in the state-machine process exposing counters/histograms.
- Expose metrics on port 9107 with basic auth controlled via `.env`.
- Keep logging enabled but treat logs as secondary evidence; metrics drive alerts.

## Consequences
- CI pipelines scrape the exporter during integration tests.
- Additional dependency on `prometheus_client` library.
- Must ensure synthetic data only; exporter scrubbed of subscriber PII.
