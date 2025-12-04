# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | Missing API key enforcement in prod | Medium | High | Integration test TC-POC-03; fail deploy if missing. |
| R2 | Latency spikes under load | Medium | Medium | Autoscaling policy and load tests; alert on p95. |
| R3 | Data loss due to in-memory store | Low | Medium | Use Postgres overlay in stage/prod; persistence tests. |
