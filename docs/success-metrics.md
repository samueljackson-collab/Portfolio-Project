# Success Metrics and Operational Practices

## Success Metrics
The portfolio analytics stack blends Matomo for behavioral telemetry, n8n for orchestration, and lightweight storage exports so that every key performance indicator (KPI) is transparent and actionable.

| Metric | Data Source | Dashboard/Query | Refresh Cadence | Owner | Alert Threshold |
| --- | --- | --- | --- | --- | --- |
| Portfolio Sessions (Rolling 7d) | Matomo Site ID `5` (Portfolio) | Matomo dashboard "Portfolio – Engagement" → widget `VisitsSummary.getVisits` filtered to segment `country==US` | Hourly archive; dashboard auto-refresh every 15 min | Analytics Engineer | Alert when 7d sessions drop >20% vs. prior 7d |
| Contact CTA Conversion Rate | Matomo goal `contact_form_submit` | Matomo "Goals" report query: `index.php?module=API&method=Goals.get` with `idGoal=3&idSite=5&period=day` | n8n scheduled fetch every 6 hours | Growth Lead | Alert when conversion rate <2.5% for 3 consecutive runs |
| Newsletter Sign-ups | Matomo event category `Newsletter`, action `Signup`; fallback CSV export in S3 bucket `portfolio-analytics/newsletter` | n8n workflow `Matomo Newsletter Sync` pushes counts to Google Sheet `Portfolio KPIs!B:B` | n8n event-driven via Matomo webhook (real time) with nightly reconciliation | Marketing Ops | Alert when daily sign-ups <5 or webhook delivery fails twice |
| Repository Stars Referenced From Portfolio | GitHub REST API `GET /repos/sams-jackson/portfolio-project` stars count correlated with Matomo referrer logs | n8n workflow `GitHub Star Monitor` merges Matomo `Referrers.getWebsites` output into Looker Studio chart `Portfolio Acquisition` | n8n cron @ 02:00 UTC daily | Analytics Engineer | Alert when GitHub stars growth <1 over 14d while sessions > previous period |
| Page Performance (LCP) | Matomo custom dimension `lcp_ms` captured via browser timing plugin | Matomo custom report `Performance → LCP Distribution` (API: `module=API&method=CustomReports.getReport&idCustomReport=4`) | Real-time via Matomo tracking; n8n hourly summary | Site Reliability Engineer | Alert when median LCP >2500 ms for 2 consecutive summaries |

## Alerting Workflow
Alerting chains combine Matomo's Custom Alerts plugin with n8n orchestrations that relay actionable notifications into Slack:

1. **Matomo Custom Alert definitions** target each KPI's API query. Example payload when created via API:
   ```bash
   curl -X POST "https://matomo.example.com/index.php" \
     -d "module=API" \
     -d "method=CustomAlerts.addAlert" \
     -d "idSite=5" \
     -d "name=Portfolio Sessions Drop" \
     -d "metric=nb_visits" \
     -d "reportUniqueId=VisitsSummary_get" \
     -d "reportCondition=decrease_more" \
     -d "reportThreshold=20" \
     -d "reportComparison=previous_period" \
     -d "alertTrigger=webhook" \
     -d "webhookUrl=https://automation.example.com/webhook/matomo/portfolio-sessions" \
     -d "token_auth=${MATOMO_API_TOKEN}"
   ```
2. **Matomo webhook → n8n**: The webhook URL points at the n8n `Matomo Alert Router` workflow webhook node (`POST https://automation.example.com/webhook/matomo/:alertKey`). The workflow performs payload validation, enriches with latest KPI snapshot (`Matomo` node hitting the relevant API endpoint), and emits structured context.
3. **n8n workflow → Slack**: The workflow posts to Slack via the [Slack Webhook node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.slack/#incoming-webhook). Minimal JSON used for templated alerts:
   ```json
   {
     "text": "*:rotating_light: Portfolio Sessions Drop*\n7d sessions fell ${payload.delta}% vs. prior week. Investigate dashboards: ${payload.dashboardUrl}",
     "channel": "#analytics-alerts",
     "username": "matomo-bot"
   }
   ```
4. **Secondary channels**: Critical alerts (e.g., LCP threshold breaches) trigger an n8n IF node that opens a PagerDuty incident through the PagerDuty Events API v2 endpoint `POST https://events.pagerduty.com/v2/enqueue` when severity is "critical".

n8n workflow configuration is versioned via the `automation/portfolio-alerts.json` export and checked into the infrastructure repository to ensure reproducibility.

## Review Rituals
- **Weekly KPI Stand-up (Mondays, led by Analytics Engineer):** 15-minute review of Matomo dashboard deltas, alert history from n8n, and backlog items created from incidents. Action items assigned in Linear.
- **Monthly Growth + Marketing Sync (First Thursday):** Growth Lead and Marketing Ops compare KPI trends against campaign calendars, validate conversion assumptions, and reprioritize experiments.
- **Quarterly Instrumentation Audit (First week of quarter):** Cross-functional session (Analytics, SRE, Marketing) to assess tracking coverage, retire unused KPIs, and plan instrumentation upgrades.

## Data Quality and Backup Verification
- **Instrumentation Validation:**
  - Run Matomo Tag Manager preview weekly to confirm event tags fire with expected categories/actions and that custom dimension `lcp_ms` captures numeric values.
  - Cross-check Matomo visit counts against Nginx access logs (GoAccess report) for ±5% tolerance.
  - Execute n8n test workflows that replay synthetic Matomo payloads to ensure parsing logic handles edge cases.
- **Data Freshness Monitoring:** n8n workflow `Matomo ETL Healthcheck` pings `module=API&method=CoreAdminHome.getSystemSummary` hourly; failures create "Data Freshness" alerts before KPI breaches occur.
- **Backup & Restore Drills:**
  - Matomo MariaDB nightly dumps stored in S3 bucket `s3://portfolio-analytics/backups/matomo/%Y/%m/%d/`. Weekly verification restores to staging and runs checksum against production table counts.
  - n8n exports (`n8n export:workflow --id <id>`) stored in Git and mirrored to S3; monthly restore test ensures compatibility after upgrades.
  - Google Sheet `Portfolio KPIs` version history exported weekly as CSV to ensure offline availability.
- **Access & Permissions Review:** Quarterly audit of Matomo and n8n API tokens; rotate secrets in the `.env` vault, invalidate unused tokens, and document changes in the security changelog.
