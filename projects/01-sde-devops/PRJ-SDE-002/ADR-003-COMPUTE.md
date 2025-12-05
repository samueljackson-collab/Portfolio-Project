# ADR-003: Compute & Deployment Model

## Status
Accepted

## Context
The stack must balance reliability with homelab resource constraints. Running everything on a single VM risks noisy-neighbor issues; full Kubernetes is heavy for small deployments.

## Decision
- Deploy Prometheus, Alertmanager, Loki, and Grafana on a **dedicated monitoring VM** with SSD storage and 8–16GB RAM.
- Run **PBS** on a separate VM with direct-attached or NFS/SMB storage to isolate backup performance from monitoring workloads.
- Containerize services via **docker-compose** (existing repo) for portability; consider migration to Kubernetes only if scale/HA demands increase.
- Pin service resources (CPU/memory limits) and enable systemd units with health checks and restart policies.

## Consequences
- Pros: Clear separation of monitoring vs. backup IO, simpler operations than Kubernetes, rapid recovery via VM restore.
- Cons: Single-VM monitoring plane is a potential SPOF; compose lacks native autoscaling.
- Follow-ups: Evaluate Thanos/Cortex for remote write and HA Prometheus; add secondary PBS target for offsite copies.
