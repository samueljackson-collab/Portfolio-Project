# Operational Playbook

## Feature flag rollout
1. Enable `ROAMING_DEMO` flag in staging and run `make compose-test`.
2. Monitor `roaming_events_processed_total` and Kafka lag for 10 minutes.
3. Promote to production with 10% traffic slice; rollback via `FF_ROAMING_DEMO=off` env var.

## Incident triage
- Check alert: `RoamingConsumerHighLag` or `RoamingAnomalySpike`.
- Run `RUNBOOKS/check-lag.md` first; if DB saturation, execute `RUNBOOKS/scale-consumer.md`.
- Capture timeline in `REPORT_TEMPLATES/incident_report.md`.

## Communications
- Status channel: `#roaming-ops`.
- PagerDuty service: `roaming-sim-prod`.
- External update cadence: every 20 minutes during SEV-1.
