# Incident Response Runbook

## Severity Levels

| Severity | Criteria | Response Time |
| --- | --- | --- |
| SEV-1 | Full outage or data loss | 15 minutes |
| SEV-2 | Partial outage, degraded performance | 30 minutes |
| SEV-3 | Minor bug, workaround available | 1 business day |

## Initial Response

1. Acknowledge PagerDuty alert.
2. Form incident command structure (IC, Ops, Comms).
3. Create Slack channel `#inc-<timestamp>` and link Jira incident ticket.

## Triage Checklist

- Review Grafana dashboards from [`monitoring/prometheus/dashboards/portfolio-overview.json`](../../monitoring/prometheus/dashboards/portfolio-overview.json).
- Inspect recent deploys via GitHub Actions.
- Check AWS Health Dashboard for regional events.

## Containment

- Roll back using `kubectl rollout undo` or `./scripts/teardown.sh --env <env>` depending on severity.
- Block malicious traffic via AWS WAF (see [`documentation/runbooks/waf-tuning.md`](./waf-tuning.md)).

## Eradication & Recovery

- Apply fixes and redeploy with [`scripts/deploy.sh`](../../scripts/deploy.sh).
- Validate with [`scripts/smoke-test.sh`](../../scripts/smoke-test.sh).
- Run [`documentation/runbooks/data-validation.md`](./data-validation.md) for data integrity.

## Post-Incident

- Schedule post-incident review within 5 business days.
- Archive artifacts in `documentation/security/post-incident-reviews/`.
- Update runbooks and monitoring thresholds based on lessons learned.
