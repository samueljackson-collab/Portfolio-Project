# Chaos Testing Guide

This guide describes the experiments used to validate resiliency assumptions documented in [ARCHITECTURE.md](../ARCHITECTURE.md#resiliency-considerations).

## Experiments

| Experiment | Tooling | Success Criteria |
| --- | --- | --- |
| API Pod Disruption | `kubectl` eviction + chaos-mesh | Requests reroute with <5% error rate and HPA restores capacity within 2 minutes. |
| Database Failover | AWS Fault Injection Simulator | Aurora promotes replica within 60 seconds; application reconnects automatically. |
| Queue Latency Spike | k6 + SQS latency injection | Worker autoscaling increases concurrency and backlog drains within 10 minutes. |

## Schedule

- Run chaos experiments in staging monthly.
- Run critical scenarios (database failover) in production quarterly with change-management approval.

## Runbook Integration

Each experiment links to an incident response runbook in [`documentation/runbooks/`](./runbooks/). Post-experiment reports are stored in `documentation/security/chaos-reports/` and referenced during quarterly resilience reviews.
