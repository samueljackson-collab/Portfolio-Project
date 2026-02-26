# Operations Runbook

## Deployment
- Deploy orchestrator as containerized service with autoscaling policies.
- Validate LLM provider connectivity and fallback models prior to release.
- Run redaction regression tests against synthetic sensitive data.

## Monitoring & Alerting
- Track generation success rate, reviewer approval time, and doc freshness score.
- Alert on elevated hallucination risk metrics or redaction failures.
- Monitor inference cost budgets and API latency.

## Rollback Procedures
- Disable automated publishing and revert to manual docs while issues resolved.
- Roll back to previous orchestrator container image and prompt set.
- Notify compliance teams if content exposure is suspected.

## Service Level Objectives
- 95% of doc drafts generated within 2 hours of new commits.
- <5% reviewer rejection rate due to inaccuracies.
- 99.5% availability for review console.
