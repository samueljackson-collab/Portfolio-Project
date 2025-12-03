# Risk Register — P07

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | PCAP contains sensitive patterns | High | Medium | QA Lead | Run scrubber + limit retention to 30 days | Open |
| R2 | Metrics exporter exposes port publicly | Medium | Low | Dev Lead | Restrict to localhost/k8s ClusterIP; add auth | Mitigated |
| R3 | Billing emulator divergence from real flow | Medium | Medium | Product | Regularly review against GSMA specs; add regression tests | Open |
| R4 | Latency injection left enabled in prod demo | Low | Medium | SRE | Default chaos off; pre-flight check in runbook | Open |
