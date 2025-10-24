# Cloud Security Posture Scanner

## Overview
Python CLI that scans AWS accounts for common security misconfigurations and drift. Implements continuous compliance checks mapped to CIS and internal policies.

## Capabilities
- Enumerates IAM, S3, EC2, RDS, Lambda, and networking resources for insecure configurations.
- Supports rule packs defined in YAML; easy to extend with new checks.
- Integrates with AWS Security Hub and Config to reconcile findings.
- Generates HTML/PDF reports and pushes findings to Slack/Jira.

## Usage
1. Install: `poetry install`.
2. Configure credentials via AWS SSO profile or assume role.
3. Run baseline scan: `poetry run scanner scan --profile prod --rules rules/cis.yaml`.
4. Schedule periodic runs via AWS Step Functions or GitHub Actions.

## Observability & Ops
- Metrics exported to CloudWatch (`findings_total`, `critical_findings`).
- Runbook details remediation workflow, SLA targets, and exception process.
- Evidence stored under `reports/YYYY/MM/` for audits.

## Security Considerations
- Uses read-only IAM role with least privilege.
- Sensitive data sanitized before logging.
- Supports encryption of reports using KMS.

