---
title: SOP: Backup and Replication
description: - Daily snapshots exported from primary region and copied to secondary bucket `multi-region-backup`. - Verify checksum using `jobs/sync.sh --verify`. - Retain 30 days of backups; enforce object lock t
tags: [documentation, portfolio]
path: portfolio/p10-multi-region/backups
created: 2026-03-08T22:19:14.028017+00:00
updated: 2026-03-08T22:04:38.132902+00:00
---

# SOP: Backup and Replication

- Daily snapshots exported from primary region and copied to secondary bucket `multi-region-backup`.
- Verify checksum using `jobs/sync.sh --verify`.
- Retain 30 days of backups; enforce object lock to prevent deletion.
- Test restore monthly using `producer/failover_sim.py --restore`.
