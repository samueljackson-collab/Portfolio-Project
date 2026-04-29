# Operations Runbook

## Deployment
- Use blue/green deployments for portal UI and API with automated smoke tests.
- Run contract tests against integration hub connectors prior to release.
- Update service catalog schemas via migration scripts tracked in Git.

## Monitoring & Alerting
- Track request throughput, completion times, and failure reasons.
- Monitor user satisfaction via in-portal surveys and NPS scoring.
- Alert on provisioning queue backlogs and integration errors.

## Rollback Procedures
- Flip traffic to previous portal version if new release fails health checks.
- Revert workflow definitions using versioned templates in Git.
- Communicate rollback status via engineering announcements channel.

## Service Level Objectives
- 99.9% availability for portal APIs.
- <30 minutes median fulfillment time for sandbox requests.
- <1% failed provisioning requests per week.
