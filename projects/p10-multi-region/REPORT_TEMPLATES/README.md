# Report Templates — P10

## Failover Drill Report
- Drill ID, date, initiator, regions involved.
- Timeline of events (failure injection, DNS changes, recovery).
- Metrics: time-to-failover, replica lag, error rates, user impact.
- Evidence links: Route 53 health-check screenshots, terraform state outputs, logs.

## Change Record
- Terraform plan summary for each region.
- Risk assessment, rollback steps, approvals.

## Post-Incident Review
- Root cause, contributing factors, detection quality.
- Action items with due dates and owners.
