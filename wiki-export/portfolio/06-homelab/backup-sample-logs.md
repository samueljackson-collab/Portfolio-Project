---
title: Backup Sample Logs
description: Sanitized excerpts from Proxmox Backup Server and TrueNAS replication logs. 2025-10-28 02:00:07 INFO: starting backup job 'daily-core-services' 2025-10-28 02:01:12 INFO: VM 104 (wikijs) backup started
tags: [documentation, portfolio]
path: portfolio/06-homelab/backup-sample-logs
created: 2026-03-08T22:19:13.057261+00:00
updated: 2026-03-08T22:04:38.348902+00:00
---

# Backup Sample Logs

Sanitized excerpts from Proxmox Backup Server and TrueNAS replication logs.

## PBS Job Excerpt (Sanitized)
```
2025-10-28 02:00:07 INFO: starting backup job 'daily-core-services'
2025-10-28 02:01:12 INFO: VM 104 (wikijs) backup started
2025-10-28 02:04:58 INFO: VM 104 (wikijs) backup finished (size=12.7GB, duration=226s)
2025-10-28 02:05:11 INFO: VM 106 (homeassistant) backup started
2025-10-28 02:08:49 INFO: VM 106 (homeassistant) backup finished (size=10.5GB, duration=218s)
2025-10-28 02:09:03 INFO: CT 201 (monitoring) backup started
2025-10-28 02:11:40 INFO: CT 201 (monitoring) backup finished (size=5.6GB, duration=157s)
2025-10-28 02:12:02 INFO: backup job 'daily-core-services' completed successfully
```

## PBS Verification Excerpt (Sanitized)
```
2025-10-28 03:30:15 INFO: verify datastore 'pbs-core' (chunk verification)
2025-10-28 03:31:02 INFO: verified 15,832 chunks (0 errors)
2025-10-28 03:31:02 INFO: verification completed successfully
```

## TrueNAS Replication Excerpt (Sanitized)
```
2025-10-28 04:00:00 INFO: Starting replication task: tank/proxmox -> dr-proxmox
2025-10-28 04:12:37 INFO: Sent 28.4GB incremental stream
2025-10-28 04:12:38 INFO: Replication task completed successfully
```
