# Threat Model
- Split-brain risk: mitigate with health checks and quorum-based router decision.
- Unauthorized failover: restrict router control to signed requests.
- Data inconsistency: rely on idempotent writes and eventual reconciliation job.
