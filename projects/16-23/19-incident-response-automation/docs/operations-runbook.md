# Operations Runbook

## Deployment
- Deploy automation services via container platform with canary releases.
- Validate webhook subscriptions and API credentials post-deploy.
- Run synthetic alert to confirm end-to-end channel creation.

## Monitoring & Alerting
- Track automation success rate, enrichment latency, and bot response times.
- Alert on failed playbook executions or missing stakeholder notifications.
- Review monthly incident metrics for regression in MTTA/MTTR.

## Rollback Procedures
- Scale down new automation version and redeploy prior container image.
- Disable newly introduced playbooks while investigating issues.
- Communicate rollback to on-call roster via incident management platform.

## Service Level Objectives
- 99.9% availability for automation services.
- <60 seconds time to produce enriched context after alert receipt.
- <1% automation failure rate per week.
