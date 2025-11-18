# Incident Response Checklist

1. **Detect** – Confirm alert and gather initial context (timestamp, service impact).
2. **Triage** – Assign an incident commander and scribe, determine severity.
3. **Mitigate** – Apply immediate mitigations (rollback, scale, feature flag).
4. **Communicate** – Notify stakeholders via status channel and update every 30 minutes.
5. **Investigate** – Review logs in Loki, metrics in Grafana, and traces if available.
6. **Recover** – Restore affected services, validate with smoke tests.
7. **Document** – Capture timeline, contributing factors, and corrective actions in post-incident report.
8. **Follow-up** – Create issues for long-term fixes and schedule retrospective within 48 hours.

