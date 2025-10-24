# ADR 0003: Observability Stack Selection

- **Status:** Accepted
- **Date:** 2025-10-11

## Context
The platform requires consolidated metrics, logs, and dashboards to support SRE workflows. Multiple stacks were considered, including AWS native tooling and open-source alternatives.

## Decision
Adopt the Prometheus + Grafana + Loki stack for observability. These tools align with CNCF standards, support Kubernetes-native deployments, and integrate with Alertmanager for incident response.

## Consequences
- ✅ Open-source stack avoids licensing costs and fits portfolio demonstration goals.
- ✅ Wide community adoption with rich ecosystem of exporters and dashboards.
- ⚠️ Requires operational expertise to scale storage and retention appropriately.

