# Project 23: Advanced Monitoring & Observability

## Overview
Unified observability stack with Prometheus, Tempo, Loki, and Grafana dashboards for portfolio workloads.

## Highlights
- `dashboards/portfolio.json` – Grafana dashboard visualizing SLOs, burn rates, and release markers.
- `alerts/portfolio_rules.yml` – Prometheus alerting rules with time-windowed burn rate calculations.
- `manifests/` – Kustomize overlays for staging/production clusters.

## Phase 1 Architecture Diagram

![Advanced Monitoring & Observability – Phase 1](render locally to PNG; output is .gitignored)

- **Context**: Cluster and application telemetry feed Prometheus, Loki, and the OpenTelemetry Collector, with Alertmanager routing incidents to chat and ticketing channels.
- **Decision**: Keep telemetry sources, observability stack, and escalation tooling in separate trust boundaries so data ingestion, storage, and paging can scale and be governed independently.
- **Consequences**: Dashboards and alerts stay aligned to a single data plane, while routing rules cleanly fan out to ChatOps and ServiceNow. Edit the [Mermaid source](assets/diagrams/architecture.mmd) alongside the PNG for future changes.
