# Risk Register — P09

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Demo API deployed without auth | Medium | Medium | Product | Enable API key middleware; restrict ingress | Open |
| R2 | In-memory queue loses messages | Medium | High | Eng Lead | Accept for POC; backlog item to use Redis/SQS | Open |
| R3 | Dependency vulnerability | High | Medium | Dev Lead | Run `pip-audit` + container scans in CI | Mitigated |
| R4 | Logs leak user data | Medium | Low | QA Lead | Ensure structured logging excludes payloads | Open |
