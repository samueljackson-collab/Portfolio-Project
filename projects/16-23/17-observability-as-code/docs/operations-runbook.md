# Operations Runbook

## Deployment
- Use GitOps merge to main to trigger Terraform apply with change approval gates.
- Monitor apply logs for drift detection and record change tickets automatically.
- Validate dashboards render expected data post-deploy using screenshot diffing.

## Monitoring & Alerting
- Track module adoption, failed lint counts, and alert coverage per service tier.
- Alert on collector queue depth, exporter error rates, and policy engine latency.
- Publish weekly SLO health report summarizing burn rates and incidents.

## Rollback Procedures
- Re-run Terraform with previous version tags to revert infrastructure changes.
- Disable newly added alerts or dashboards via feature flags when necessary.
- Document rollback outcomes in change log with follow-up actions.

## Service Level Objectives
- 99.9% availability for policy engine and module registry.
- <2 hours time-to-detect missing telemetry coverage after onboarding.
- Zero unauthorized configuration changes (enforced via CI).
