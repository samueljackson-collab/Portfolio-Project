# Operations Runbook

## Deployment
- Deploy collectors via serverless functions with staggered schedules.
- Apply infrastructure-as-code for normalization store and workflow services.
- Test audit portal authentication and encryption prior to launches.

## Monitoring & Alerting
- Track evidence freshness, collector success rates, and workflow SLA adherence.
- Alert on overdue controls, failed exports, and unauthorized access attempts.
- Review storage integrity via periodic hash verification.

## Rollback Procedures
- Disable problematic collectors while investigating data quality issues.
- Restore previous schema versions via migration scripts and backups.
- Communicate rollback status to compliance and audit stakeholders.

## Service Level Objectives
- Evidence freshness under 24 hours for automated controls.
- <1% collector failure rate per run.
- 100% audit trail completeness for approvals and access.
