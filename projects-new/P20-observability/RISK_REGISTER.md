# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Prometheus TSDB corruption | High | Low | Snapshots and WAL cleanup | SRE |
| High cardinality metrics | Medium | Medium | Recording rules and limiters | Observability |
| Receiver secrets leaked | High | Low | Store in env vars + secret manager | Security |
