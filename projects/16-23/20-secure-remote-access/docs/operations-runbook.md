# Operations Runbook

## Deployment
- Leverage infrastructure-as-code to roll out additional gateways across regions.
- Validate SSO integration, MFA prompts, and device checks during canary releases.
- Run traffic replay tests to ensure application compatibility.

## Monitoring & Alerting
- Observe gateway CPU/memory, session counts, and auth success rate.
- Alert on failed posture checks spikes or unusual geographic access patterns.
- Review audit pipeline delivery latency and SIEM ingestion status.

## Rollback Procedures
- Fail back to previous gateway images via blue/green deployment.
- Temporarily relax policies for critical access while investigating issues.
- Notify security operations and impacted teams of rollback rationale and remediation steps.

## Service Level Objectives
- 99.95% availability for access gateways.
- <30 seconds average authentication time including posture checks.
- 100% session logging coverage for privileged systems.
