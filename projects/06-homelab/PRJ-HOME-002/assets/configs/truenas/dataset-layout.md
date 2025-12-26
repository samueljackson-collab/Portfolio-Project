# TrueNAS Dataset Layout

Dataset layout for PRJ-HOME-002 with purpose and retention notes. All names and addresses are sanitized.

| Dataset                     | Mountpoint                  | Purpose                               | Notes                             |
|-----------------------------|-----------------------------|---------------------------------------|-----------------------------------|
| `pool1/apps`                | `/mnt/pool1/apps`           | Application configs (Wiki.js, HA)     | Nightly snapshots, 14-day retain  |
| `pool1/media`               | `/mnt/pool1/media`          | Immich media storage                  | Weekly replication to offsite     |
| `pool1/backups/pbs`         | `/mnt/pool1/backups/pbs`    | Proxmox Backup Server datastore copy  | Immutable snapshots, 90-day retain|
| `pool1/backups/logs`        | `/mnt/pool1/backups/logs`   | Exported backup logs                  | Compressed monthly archives       |
| `pool1/isos`                | `/mnt/pool1/isos`           | ISO/templates repository              | Read-only share                   |
| `pool1/audit`               | `/mnt/pool1/audit`          | Incident evidence export              | Access limited to admins          |
| `pool1/homelab-share`       | `/mnt/pool1/homelab-share`  | General NFS share for tools           | Snapshot before major upgrades    |

- All datasets inherit compression (lz4) and atime=off.
- Encryption keys stored offline; swap to new keys during annual rotation.
- Replication to offsite occurs Sundays at 02:00 via SSH transport.
