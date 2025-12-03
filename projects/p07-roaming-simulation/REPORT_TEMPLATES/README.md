# Report Templates — P07

## Test Execution Summary
- **Header:** Run ID, date/time, engineer, git SHA, environment (`dev|ci|perf`).
- **Metrics:** total scenarios, pass/fail counts, mean/95p attach latency, retry counts, PCAP size.
- **Notable events:** roaming denials, billing anomalies, failed MAP transactions.
- **Evidence:** links to JUnit XML, coverage, PCAP bundle, screenshots (Grafana, Loki queries).

## Incident Timeline
- **Detection:** alert name, time, detector (Prometheus/Loki), impacted subscriber count.
- **Timeline:** minute-by-minute events, commands run, configuration changes.
- **Remediation:** steps executed, result, verification.
- **Follow-up:** backlog items, ADR references, ownership.

## Compliance Log (PII-free)
- **Data sources:** synthetic IMSI/MSISDN datasets only.
- **Retention:** PCAPs 30 days, audit logs 90 days.
- **Rotation evidence:** include rotation job output from `jobs/rotate-logs.py`.
