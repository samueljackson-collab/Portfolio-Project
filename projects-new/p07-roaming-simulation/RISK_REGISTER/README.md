# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | Misconfigured impairment profiles causing false alerts | Medium | Medium | Peer-review profile changes; use canary overlay. |
| R2 | PII leakage in logs | Low | High | Hash IMSI/MSISDN, restrict log access, periodic audits. |
| R3 | gRPC certificate expiry | Medium | High | Automate renewal with 60-day alarm; validate in CI. |
| R4 | Replay attack inflating KPIs | Low | Medium | Enforce nonce/timestamp validation and rate limits. |
