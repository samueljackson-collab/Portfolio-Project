# Backup Rotation Policy

| Tier | Scope | Frequency | Retention | Verification |
| --- | --- | --- | --- | --- |
| Local Snapshots | All Proxmox VMs | Every 6 hours | 48 hours | Automated checksum validation |
| Remote Sync | TrueNAS dataset replication | Nightly | 14 days | Weekly `zfs scrub` report review |
| Cloud Archive | Encrypted Borg to B2 | Weekly | 12 months | Monthly restore test to isolated VLAN |

## Restore Validation Steps
1. Trigger restore of latest Borg archive to staging dataset.
2. Attach restored disk to test VM and boot.
3. Run application smoke tests (login, CRUD, upload) to confirm integrity.
4. File post-mortem if any validation step fails.
