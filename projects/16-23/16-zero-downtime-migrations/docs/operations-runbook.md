# Operations Runbook

## Deployment
- Trigger orchestrator deployment via GitOps workflow to staging then production.
- Run smoke tests ensuring orchestrator API and UI respond within SLA.
- Validate shadow validator connectivity to both blue and green stacks before enabling traffic shaping.

## Monitoring & Alerting
- Golden signals: migration duration, validation failure rate, traffic split health, rollback frequency.
- Alert thresholds: validation failure > 0.5% for 5 min, rollback initiated, orchestrator API latency > 500 ms.
- Dashboards segmented per service with pre/post metrics and customer impact overlay.

## Rollback Procedures
- Initiate orchestrator rollback command; confirm traffic shaper routes 100% to previous stack.
- Revert schema migrations via automatically generated down scripts.
- Run post-rollback data integrity checks and notify stakeholders in incident channel.

## Service Level Objectives
- 99.95% orchestrator availability.
- <5 minutes mean time to rollback.
- <0.2% customer error rate during migration windows.
