# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | Secrets accidentally committed | Low | High | Use env templates only; pre-commit secret scan. |
| R2 | Flaky mock data causing noise | Medium | Medium | Reset data before runs; lock snapshots. |
| R3 | Schema drift ignored | Medium | High | Blocking contract tests; alerting via `api_contract_drift_total`. |
| R4 | Performance regressions hidden | Low | Medium | Track `api_latency_p95_ms` and fail if > threshold. |
