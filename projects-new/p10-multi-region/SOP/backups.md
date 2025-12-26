# SOP: Backup and Replication

- Daily snapshots exported from primary region and copied to secondary bucket `multi-region-backup`.
- Verify checksum using `jobs/sync.sh --verify`.
- Retain 30 days of backups; enforce object lock to prevent deletion.
- Test restore monthly using `producer/failover_sim.py --restore`.
