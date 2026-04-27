# Reporting Package

## Reporting Cadence
- **Weekly:** Health summary (uptime, latency, error rate), cost snapshot, and change log.
- **Monthly:** SLO attainment, incident postmortems, capacity trends, and security posture updates.
- **Quarterly:** Architecture/ADR review, DR drill results, roadmap alignment with business KPIs.

## Report Templates
### Weekly Health Report
- **Scope:** Deployments completed, incidents, test coverage, cost variances.
- **Inputs:** CloudWatch dashboards, CI artifacts, AWS Cost Explorer exports.
- **Format:** 1-page PDF/Markdown stored in `reports/weekly/` with charts and action items.

### Monthly SLO Report
- **Metrics:** Availability (%), latency (p95), error budget burn, MTTR, change fail rate.
- **Analysis:** Compare against targets; highlight regressions and remediation plans.
- **Distribution:** Engineering leadership, product owners, and platform team.

### Security Posture Report
- **Findings:** Vulnerability scan results, secrets scans, IAM drift, WAF rule hits.
- **Risk Impact:** Map to risk register IDs with owner and due dates.
- **Approvals:** Security lead and service owner sign-off.

## Data Sources & Automation
- **Metrics:** CloudWatch GetMetricData, RDS Performance Insights, ALB access logs to S3 + Athena queries.
- **Costs:** AWS Cost Explorer API; `infra/cost-estimator` outputs from Terraform plans.
- **Tests:** CI pipelines upload JUnit/coverage HTML; summarized via GitHub PR comments.
- **Incidents:** PagerDuty/Slack exports; stored as Markdown with timelines and lessons learned.

## Distribution & Governance
- **Storage:** `reports/` version-controlled; PDFs generated from Markdown for stakeholders.
- **Access:** Read-only for broader org; write access restricted to platform team.
- **Approvals:** Reports reviewed in weekly ops review; action items tracked in backlog with SLA.
- **KPIs Tracked:** Uptime, latency, throughput, cost per tenant, lead time for changes, change failure rate, security findings count, DR readiness score.
