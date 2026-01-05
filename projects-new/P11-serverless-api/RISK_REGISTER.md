# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Cold starts during traffic spikes | High | Medium | Provisioned concurrency on hot paths; pre-warm via scheduled invocation | Platform |
| Misconfigured IAM leading to data exposure | Critical | Low | Least-privilege roles, automated IAM Access Analyzer checks | Security |
| DynamoDB hot partitions | High | Medium | Use hashed partition keys, adaptive capacity metrics alarms | Data |
| EventBridge consumer failures | Medium | Medium | Dead-letter queues with replay script `scripts/replay_dlq.py` | DevOps |
