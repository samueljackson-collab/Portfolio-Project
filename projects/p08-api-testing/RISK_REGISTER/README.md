# Risk Register — P08

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Real tokens leaked in environments | High | Low | QA Lead | Enforce `.example` only; pre-commit secret scan | Mitigated |
| R2 | Schema drift undetected | Medium | Medium | Test Lead | Contract tests + coverage matrix | Open |
| R3 | Reports contain PII | Medium | Medium | Dev Lead | Use sanitization script and redaction flags | Open |
| R4 | Mock server abused for injections | Low | Medium | SRE | Bind to localhost; network policy in CI | Open |
