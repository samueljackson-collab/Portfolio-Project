# Booking Outage Incident Playbook

## Scope
Applies to partial or full outages impacting booking flows on the tours or resort sites.

## Detection
- Synthetic transaction failure in Playwright suite.
- Payment provider webhook backlog exceeding 50 pending events.
- Customer support escalation referencing booking failures.

## First Response
1. Assign incident commander and communications lead.
2. Pause promotional campaigns to reduce new traffic.
3. Confirm issue via staging replication if safe to do so.

## Triage Checklist
- Check payment gateway status dashboard.
- Query booking API health endpoint (`/healthz`).
- Inspect recent deploys and feature flags.
- Validate database connectivity and replication lag.

## Communication
- Post updates every 15 minutes in #incident channel.
- Email stakeholders if outage exceeds 30 minutes.
- Prepare post-incident summary within 24 hours.

## Recovery
- Rollback to previous release using `deploy rollback --service booking`.
- Clear failed bookings queue and reprocess after fix.
- Run smoke tests (search, add-to-cart, checkout) before declaring resolved.

## Post-Incident
- Capture timeline, customer impact, root cause, remediation tasks.
- File Jira actions for permanent fixes and playbook adjustments.
