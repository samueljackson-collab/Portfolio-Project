# Platform Observability Mesh

- **Role Category:** DevOps / SRE
- **Status:** Completed

## Executive Summary
Unified logs, metrics, and traces with opinionated defaults and developer self-service dashboards.

## Scenario & Scope
Multi-cluster setup with shared observability stack and tenant isolation.

## Responsibilities
- Deployed distributed tracing
- Normalized logs and metrics schemas
- Built golden signal dashboards

## Tools & Technologies
- OpenTelemetry
- Tempo
- Loki
- Prometheus
- Grafana

## Architecture Notes
Control plane cluster hosts observability stack; tenants onboard via Helm charts with scoped credentials.

## Process Walkthrough
- Set up OTel collectors and exporters
- Enabled tracing libraries for services
- Created reusable dashboard templates
- Documented tenant onboarding steps

## Outcomes & Metrics
- Achieved trace coverage for 90% of services
- Standardized log labels across clusters
- Reduced triage time via golden dashboards

## Evidence Links
- observability/p-devops-03/mesh.md

## Reproduction Steps
- Deploy the observability stack via Helmfile
- Install OTel collectors per cluster
- Instrument sample services and verify dashboards

## Interview Points
- Multi-tenant observability design
- Tradeoffs between push vs pull metrics
- Rollout strategies for tracing
