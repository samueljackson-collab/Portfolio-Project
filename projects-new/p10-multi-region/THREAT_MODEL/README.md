# Threat Model

## Assets
- DNS records and health checks
- Replicated data snapshots
- IAM roles for replication and failover

## Threats
- DNS hijack or misconfiguration leading to traffic blackhole.
- Stale snapshots causing data loss during failover.
- Unauthorized failover trigger.

## Mitigations
- DNS change approvals and MFA for hosted zone updates.
- Automated snapshot freshness alerts.
- Signed failover toggles via pipeline with audit trail.
