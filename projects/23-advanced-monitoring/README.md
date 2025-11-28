# Project 23: Advanced Monitoring & Observability

## Overview
Unified observability stack with Prometheus, Tempo, Loki, and Grafana dashboards for portfolio workloads.

## Highlights
- Grafana dashboard visualizing SLOs, burn rates, and release markers in [`dashboards/portfolio.json`](dashboards/portfolio.json).
- Prometheus alerting rules in [`alerts/portfolio_rules.yml`](alerts/portfolio_rules.yml).
- Kustomize overlays for staging and production clusters under [`manifests/`](manifests/) with core deployment/service specs in [`manifests/base`](manifests/base) (e.g., [`manifests/base/deployment.yaml`](manifests/base/deployment.yaml)) and a production overlay in [`manifests/overlays/production/kustomization.yaml`](manifests/overlays/production/kustomization.yaml).
- CI workflow [`.github/workflows/monitoring.yml`](.github/workflows/monitoring.yml) and validation tests in [`tests/test_configs.py`](tests/test_configs.py).
- Operational procedures in [`RUNBOOK.md`](RUNBOOK.md) and additional context in [`wiki/overview.md`](wiki/overview.md).
