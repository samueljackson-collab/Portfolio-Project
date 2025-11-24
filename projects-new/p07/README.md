# P07 Roaming Simulation Platform

A production-ready blueprint for simulating telecom roaming events with synthetic subscribers, configurable network conditions, and pluggable analytics pipelines. This pack delivers runnable containers plus the operational collateral (runbooks, SOPs, ADRs, threat model, and risk register) required for enterprise readiness.

## Goals
- Generate high-fidelity roaming events for testing billing, fraud detection, and QoS systems.
- Provide reproducible workloads via containerized producers/consumers and Kubernetes manifests.
- Offer clear operational guidance: runbooks, playbooks, SOPs, and dashboards.

## Quick start
1. Build and run locally with Docker Compose:
   ```sh
   docker compose -f docker/docker-compose.yml up --build
   ```
2. Seed sample scenarios:
   ```sh
   docker exec roaming-producer python /app/jobs/load_scenarios.py --profile demo
   ```
3. Tail consumer metrics locally:
   ```sh
   docker exec roaming-consumer curl -s http://localhost:9102/metrics | head
   ```
4. Deploy to Kubernetes for CI smoke tests:
   ```sh
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/
   ```

## Repository layout
- `ARCHITECTURE.md` — system context, flows, and scaling model.
- `TESTING.md` — test strategy, cases, and data seeds.
- `REPORT_TEMPLATES/` — incident and postmortem templates.
- `PLAYBOOK.md` — high-level operational playbook for feature flagging and incident triage.
- `RUNBOOKS/` — executable steps for provisioning, recovery, and log review.
- `SOP/` — daily/weekly operational procedures.
- `METRICS/` — SLI/SLO catalog with alert thresholds.
- `ADRS/` — architecture decisions with rationale.
- `THREAT_MODEL.md` — STRIDE-style analysis with mitigations.
- `RISK_REGISTER.md` — tracked risks with owners and responses.
- `docker/` — producer, consumer, and batch job containers.
- `k8s/` — manifests for namespace-scoped deployment and observability hooks.

## Operational guardrails
- All configs are 12-factor compliant and overrideable via environment variables.
- Producers enforce idempotent message keys to avoid duplicate billing events.
- Consumers expose Prometheus metrics and structured JSON logs.
- Default dashboards and alerts assume a 3-node K8s dev cluster with horizontal pod autoscaling enabled.

## Support matrix
- Container runtime: Docker 24+
- Kubernetes: v1.28+
- Message bus: Kafka 3.5+ or Redpanda 23.2+
- Language runtimes: Python 3.11 for producers/jobs, Go 1.21 for consumer
