# Risk Register
| ID | Risk | Impact | Likelihood | Owner | Mitigation |
|----|------|--------|------------|-------|------------|
| R1 | Kafka cluster saturation during load tests | High | Medium | Platform | Autoscaling + partition tuning; pre-test capacity checks |
| R2 | Incorrect roaming tariff rules | Medium | Medium | Product | Scenario validation suite; peer review of rule changes |
| R3 | PII leakage in logs | High | Low | Security | Log scrubbing middleware; quarterly privacy audits |
| R4 | Backup job failure | High | Low | SRE | Daily backup verification alert |
