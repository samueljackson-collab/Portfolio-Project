# TrueNAS Dataset Structure
# =========================
# This document outlines the dataset and share configuration for homelab storage

## Dataset Hierarchy

```
tank/                           (Root pool)
├── backups/                    (Backup storage)
│   ├── proxmox/                (Proxmox Backup Server datastore)
│   ├── workstation/            (Desktop backups)
│   └── documents/              (Document archives)
│
├── media/                      (Media storage)
│   ├── photos/                 (Immich photo storage)
│   ├── videos/                 (Video library)
│   └── music/                  (Music library)
│
├── shares/                     (General file shares)
│   ├── home/                   (User home directories)
│   ├── documents/              (Shared documents)
│   └── software/               (Software repository)
│
├── services/                   (Service data volumes)
│   ├── wikijs/                 (Wiki.js data)
│   ├── homeassistant/          (Home Assistant config)
│   ├── postgresql/             (Database storage)
│   └── nginx/                  (Nginx configuration & cache)
│
└── iso/                        (ISO images for VM templates)
    ├── linux/
    └── windows/
```

## Dataset Properties

### Compression
```
tank/backups:      compression=lz4
tank/media:        compression=lz4
tank/shares:       compression=lz4
tank/services:     compression=zstd
tank/iso:          compression=off
```

### Snapshots
```
tank/backups:      snapshots=hourly(24), daily(7), weekly(4), monthly(3)
tank/media:        snapshots=daily(7), weekly(4), monthly(3)
tank/shares:       snapshots=hourly(24), daily(7), weekly(4)
tank/services:     snapshots=hourly(24), daily(7), weekly(4), monthly(3)
tank/iso:          snapshots=off
```

### Quotas
```
tank/backups/proxmox:        quota=2TB
tank/media/photos:           quota=500GB
tank/services/postgresql:    quota=100GB
tank/shares/home:            refquota=50GB (per user)
```

## NFS Exports

### Proxmox Nodes
```
Path: /mnt/tank/backups/proxmox
Export: /mnt/tank/backups/proxmox
Allowed Networks: 192.168.10.0/24
Options: rw,sync,no_subtree_check,root_squash
Purpose: Proxmox Backup Server datastore
```

### Service Data Volumes
```
Path: /mnt/tank/services
Export: /mnt/tank/services
Allowed Networks: 192.168.10.0/24
Options: rw,async,no_subtree_check,all_squash
Purpose: Docker volume mounts for services
```

## SMB/CIFS Shares

### User Home Directories
```
Share Name: homes
Path: /mnt/tank/shares/home
Access: Authenticated users only
Permissions: User-specific (700)
Guest Access: No
Purpose: Personal file storage
```

### Shared Documents
```
Share Name: documents
Path: /mnt/tank/shares/documents
Access: Domain Users (read/write)
Permissions: 775
Guest Access: No
Purpose: Shared documentation repository
```

### Media Libraries
```
Share Name: photos
Path: /mnt/tank/media/photos
Access: Domain Users (read), service accounts (read/write)
Permissions: 755
Guest Access: No
Purpose: Immich photo library backend
```

## iSCSI Targets

### VM Storage LUNs (if applicable)
```
Target: iqn.2024-01.local.homelab:storage.vm-storage
LUN 0: zvol/tank/iscsi/vm-storage-01 (500GB)
Allowed Initiators: pve-node1, pve-node2, pve-node3
Authentication: CHAP (username/password)
Purpose: High-performance VM storage
```

## Replication

### Offsite Backup
```
Source: tank/backups
Destination: backup-nas/tank/backups (remote)
Schedule: Daily at 03:00 AM
Retention: 7 days on remote
Transport: SSH
Purpose: Offsite disaster recovery
```

## Performance Tuning

### ARC Settings
```
ARC Max: 32GB (of 64GB total system RAM)
ARC Min: 8GB
L2ARC: 128GB NVMe cache
```

### ZIL/SLOG
```
Device: 32GB NVMe partition
Purpose: Write acceleration for sync writes
```

## Monitoring & Alerts

### Disk Health
- SMART tests: Short (weekly), Long (monthly)
- Scrub schedule: First Sunday of month
- Alert on: SMART failures, scrub errors, capacity >80%

### Dataset Alerts
- Quota warnings at 80%, 90%
- Snapshot failures
- Replication failures

## Backup Strategy

### Dataset-Level Backups
- TrueNAS configuration: Weekly export to USB
- Dataset snapshots: See snapshot schedule above
- Replication to offsite: Daily for critical datasets

### Recovery Testing
- Monthly restore test from snapshots
- Quarterly disaster recovery drill

---

## Notes

- All paths are examples from homelab.local domain
- Adjust IPs, quotas, and schedules to match your environment
- Always test restores before relying on backups
- Monitor disk health and replace proactively

## Configuration Files

For actual TrueNAS configuration exports:
1. System > General > Save Config
2. Storage > Pools > Export/Backup
3. Sharing > Export configuration

Store exports securely offsite with encryption.
