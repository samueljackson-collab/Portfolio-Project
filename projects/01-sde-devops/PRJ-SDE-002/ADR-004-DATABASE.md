# ADR-004: Storage, Backup, and Retention

## Status
Accepted

## Context
Metrics (TSDB), logs, and VM backups have different retention and performance needs. A unified store would be inefficient and risky.

## Decision
- **Prometheus:** 30-day retention on SSD; remote-write optional to Thanos for long-term storage.
- **Loki:** Store chunks on object storage or RAID; retention tiering (critical services 30d, baseline 14d, dev 7d).
- **PBS:** Nightly incremental backups with 30-day retention, weekly full verification; deduplication enabled; encryption at rest with passphrase escrowed.
- **Snapshots:** For critical VMs, enable ZFS snapshots with 7d retention to speed restores.

## Consequences
- Pros: Cost-effective storage aligned to data characteristics; faster restores via PBS; resilience via remote-write option.
- Cons: Multiple storage backends to monitor; requires periodic pruning and verification.
- Follow-ups: Add offsite PBS sync; automate restore drills; monitor object storage costs and latency.
