# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| DAG backlogs due to slow workers | SLA miss and delayed downstream jobs | Medium | Autoscale Celery workers, tune pools, and alert on queue depth | Data Eng |
| Schema drift in source files | Data corruption and failed joins | High | Great Expectations suites, contract tests, and quarantine enforcement | Data Quality |
| Credential leakage via logs | Security incident | Low | Scrub secrets in logging config, limit log access, rotate Fernet keys | Security |
| S3 cost overruns from retained staging data | Budget breach | Medium | Lifecycle policies to Glacier and `scripts/cleanup_staging.sh` | FinOps |
