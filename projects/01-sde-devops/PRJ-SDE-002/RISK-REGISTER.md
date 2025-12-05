# Risk Register — PRJ-SDE-002

| ID | Risk | Likelihood | Impact | Owner | Mitigation | Contingency |
| --- | ---- | ---------- | ------ | ----- | ---------- | ----------- |
| R1 | Exporter drift after host rebuilds causing blind spots | Medium | High | Platform | Automated discovery + CI validation of target inventory; alerts on scrape gaps | Manual sweep of hosts, redeploy exporters via Ansible |
| R2 | Misconfigured Alertmanager silences masking incidents | Medium | High | SRE Lead | Require owner/reason/expiry metadata; weekly silence audit; sandbox tests | Clear all silences, restore defaults from git, run fire drill |
| R3 | Backup storage saturation leading to failed jobs | Medium | High | Infra | Capacity alerts at 70/85%; pruning policy; offload to secondary storage | Pause non-critical backups, expand storage, temporary compression increase |
| R4 | TLS cert expiry on Grafana/Alertmanager/PBS | Low | Medium | Security | ACME automation, cert-expiry alerts | Use emergency certs, rotate secrets, schedule downtime if needed |
| R5 | Loki high cardinality causing resource exhaustion | Medium | Medium | Observability | Label hygiene guidelines, cardinality alerts, pre-prod validation | Drop offending labels, increase resources temporarily, throttle ingest |
| R6 | PBS compromise or ransomware | Low | Critical | Security | Network isolation, encryption, MFA, signed updates | Isolate PBS, restore from clean snapshot, rotate keys and credentials |
