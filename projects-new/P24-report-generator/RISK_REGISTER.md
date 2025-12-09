# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Signing key compromise | Critical | Low | Hardware-backed keys and rotation | Security |
| Bad data inputs | Medium | Medium | Schema validation before render | QA |
| Delivery failures | Medium | Medium | Retry with exponential backoff and DLQ | Ops |
