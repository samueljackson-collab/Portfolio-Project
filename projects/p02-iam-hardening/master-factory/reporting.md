# Reporting — P02 IAM Hardening Master Factory

Reporting focuses on least privilege adherence, external-access detection, and unused credential cleanup efficacy.

## Key Metrics
- **Access Analyzer findings:** Count and severity trend; time-to-remediate after `make simulate` fails.
- **MFA enforcement coverage:** Percentage of privileged roles requiring MFA; number of MFA enforcement failures per release.
- **External access drift:** New cross-account/public resources detected per sprint.
- **Unused credential cleanup:** Disabled/removed keys and roles per cycle; time idle before cleanup.

## Data Sources
- `make policy-diff` artifacts for change deltas and access expansions.
- Access Analyzer reports exported from CI/CD and IaC pipelines.
- MFA test harness outputs from `make test` and enforcement hooks.
- Cleanup job logs (keys/roles) forwarded by observability pipelines.

## Delivery Cadence
- Weekly dashboards to engineering and security leads.
- Release-level summaries attached to change tickets with Access Analyzer/MFA status.
- Quarterly audit packet including ADR excerpts, risk register, and remediation performance.
