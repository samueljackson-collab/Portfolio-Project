# Observability — P02 IAM Hardening Master Factory

Observability captures IAM signals that prove least privilege, detect external access, and surface unused credential cleanup.

## Dashboards
- **Policy Health:** Access Analyzer findings by severity, mapped to repositories and IaC stacks.
- **MFA Enforcement:** Success/failure counts for MFA-required role sessions; trends by environment.
- **Credential Hygiene:** Number of disabled keys/roles per week; age distribution before cleanup.

## Alerts
- High/medium Access Analyzer findings emitted during `make simulate` or pipeline runs.
- MFA enforcement failures on privileged roles or automation identities.
- Detection of new external principals or public bucket policies in `make policy-diff` outputs.
- Cleanup job failures or backlog growth beyond SLA.

## Logging and Tracing
- Centralize IAM change logs, Access Analyzer exports, and MFA enforcement events.
- Tag logs with PR/commit IDs to trace lineage back to code changes.
- Emit structured events from cleanup scripts to power reporting metrics.
