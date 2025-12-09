# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Workflow backlog during incidents | High | Medium | Autoscale workers and prioritize critical queues | Platform |
| Broken action releases | Medium | Medium | Canary new actions, rollback via feature flags | DevOps |
| Policy drift between stages | Medium | Medium | Promotion gates and config checks | Governance |
