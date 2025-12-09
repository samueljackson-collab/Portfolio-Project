# Architecture

## System context
- **Producer (Python)**: synthesizes roaming CDRs and signaling events, publishes to Kafka topic `roaming.events` with idempotent keys.
- **Consumer (Go)**: validates events, enriches with SIM profiles, stores aggregates in PostgreSQL, and exposes metrics on :9102.
- **Batch jobs**: periodic reconciliation and anomaly sweeps executed via CronJob.
- **Control plane**: Helm-ready manifests under `k8s/` with namespace isolation and PodSecurity standards.

```
[Mobile Device] -> [Producer] -> [Kafka/Redpanda] -> [Consumer] -> [PostgreSQL]
                                           \-> [Anomaly Job] -> [Alertmanager]
```

## Data flows
1. Producer fetches scenario templates and emits roaming events at configurable RPS.
2. Consumer validates schema via JSON Schema, enriches with SIM metadata, and writes aggregates.
3. Reconciliation job scans daily for missing TAP-in/TAP-out pairs and emits PagerDuty alerts.
4. Metrics scraped by Prometheus; Grafana dashboards live in `METRICS/grafana-dashboard.json`.

## Scaling
- **Throughput**: HorizontalPodAutoscaler based on Kafka consumer lag and CPU > 70%.
- **Storage**: TimescaleDB partitioning for 30-day hot data; S3 export via batch job for cold storage.
- **Resilience**: At-least-once semantics with idempotent keys; circuit breakers around DB writes.

## Dependencies
- Kafka or Redpanda
- PostgreSQL/TimescaleDB
- Prometheus stack
- Optional: Jaeger for tracing (service mesh ready)
