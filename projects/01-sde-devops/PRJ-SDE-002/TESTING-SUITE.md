# Testing Suite — PRJ-SDE-002

## Principles
- Automate wherever possible; gate releases on objective health checks.
- Include backup restore validation alongside monitoring tests.
- Capture artifacts (logs, screenshots of dashboards, alert fire tests) for audit.

## Test Matrix
- **Linting:** `terraform fmt/validate`, `ansible-lint`, `yamllint`, `promtool check config rules.yml`, `loki-canary` dry-run.
- **Unit-Style:** Prometheus rule unit tests with fixtures; Alertmanager routing simulation; Grafana provisioning schema validation.
- **Integration:**
  - End-to-end scrape from exporters (node, Proxmox, app exporters) with P95 latency <500ms.
  - Promtail→Loki ingest + query round-trip; verify labels present.
  - Alert fire drill to Slack/PagerDuty sandbox with inhibition and grouping behavior observed.
- **Backup & Restore:**
  - Nightly PBS job success; weekly restore of representative VM with checksum match and boot validation.
  - Snapshot restore test for critical VMs; measure RTO/RPO against targets.
- **Resilience/Chaos:**
  - Restart Prometheus/Loki containers and confirm data retention and alert continuity.
  - Network partition simulation for exporters; verify alerting on scrape failures and recovery clears.
- **Performance:**
  - Load test Loki ingest at 2k lines/sec for 10 minutes; query P95 <2s for 24h window.
  - Prometheus cardinality guardrails: reject series >10 label dimensions; alert on >5M series.

## Environments
- **Dev:** Ephemeral compose stack, fake exporters, test Slack webhook.
- **Staging:** Mirrors production data flows; used for rule tuning and restore drills.
- **Prod:** Change-controlled; alerts route to live on-call.

## Automation Hooks
- CI pipeline triggers lint + unit tests on PR.
- Nightly synthetic probes hitting dashboards, Loki queries, and Alertmanager API health.
- Weekly restore job automated via PBS API and validated through Prometheus Pushgateway metrics.

## Acceptance Gates
- No critical lint errors; rule tests pass.
- Alert fire drill evidence attached to change ticket.
- Backup restore success in last 7 days; offsite copy verified monthly.
