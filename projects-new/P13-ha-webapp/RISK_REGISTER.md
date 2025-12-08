# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Split-brain after network partition | Data inconsistency | Low | Patroni watchdogs, fencing scripts, and frequent failover drills | DBA |
| TLS expiration | Outage for TLS clients | Medium | Monitor cert expiry, automate `scripts/rotate_certs.sh`, ACME staging tests | SRE |
| Replication lag during bursts | Stale reads | Medium | Increase replication slots, tune checkpoints, alert on lag > 5s | SRE |
| Cache stampede after deploy | Latency spike | Medium | Pre-warm caches with `scripts/cache_warm.sh`, stagger rollout | App Team |
