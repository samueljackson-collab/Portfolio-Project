# Reporting Package

## Cadence
- **Weekly:** Engineering status (deployments completed, test coverage, open defects, cost variance).
- **Monthly:** Platform health review (SLO attainment, incident summaries, security findings, risk updates, cost trends).
- **Quarterly:** Executive readout (business outcomes, roadmap progress, DR drills, compliance evidence summary).

## Key Reports & Templates
1. **Deployment Log**
   - Fields: date/time, env, change ID, approvers, plan/apply hashes, success/failure, rollback details, links to artifacts.
   - Location: `reports/deployments-<yyyy-mm>.md`.
2. **SLO & Incident Report**
   - SLO compliance (%), burn rate, top offenders, incidents with root cause and actions, mean time to detect/respond/resolve.
   - Include graphs from CloudWatch dashboards and on-call load.
3. **Security Posture Report**
   - Vulnerability scan counts (critical/high/medium), secret scan results, WAF trends, IAM anomalies, open exceptions.
   - Map to controls in `SECURITY-PACKAGE.md` and track remediation SLAs.
4. **Cost & Efficiency Report**
   - Infracost deltas per change, monthly actual vs forecast, top spend drivers, rightsizing actions, savings plan coverage.
   - Budget alerts triggered and responses.
5. **Risk Register Update**
   - Current risk states, new risks, mitigations completed, accepted risks, and upcoming reviews.

## Metrics to Highlight
- Deployment frequency, lead time for changes, change failure rate, MTTR.
- SLO performance by environment; error budget spend and freeze recommendations.
- Vulnerability backlog trend; average time to remediate critical findings.
- Cost per environment and per feature; unit economics if available.

## Distribution
- **Channels:** Confluence/Notion page, Slack summary in #platform, emailed PDF to stakeholders monthly.
- **Owners:** Platform Lead curates weekly; Security Lead contributes security sections; FinOps provides cost data.
- **Storage:** Reports stored in `reports/` with versioning; sensitive data redacted; links to evidence bundles.

## Automation Hooks
- CI jobs publish terraform plan/apply artifacts and test reports to `reports/`.
- Scheduled job pulls CloudWatch metrics and WAF stats to refresh dashboards and embed snapshots in reports.
- Automated reminders for report deadlines and risk review actions.
