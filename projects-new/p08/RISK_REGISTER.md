# Risk Register
| ID | Risk | Impact | Likelihood | Owner | Mitigation |
|----|------|--------|------------|-------|------------|
| R1 | Specs drift from implementation | Medium | Medium | QA | Regenerate specs weekly; contract tests fail fast |
| R2 | Test flakiness in CI | Medium | Medium | SRE | Retry policy + flaky test quarantine |
| R3 | Secret leakage in fixtures | High | Low | Security | Secret scanning in pipeline |
