# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | Route 53 failover misconfigured | Low | High | CI linting of DNS templates; periodic drills. |
| R2 | Snapshot replication lag | Medium | High | Alert on `mr_snapshot_replication_age_seconds`; enforce RPO monitoring. |
| R3 | Secondary cold start too slow | Medium | Medium | Pre-warm secondary pods weekly; keep minimal baseline traffic. |
