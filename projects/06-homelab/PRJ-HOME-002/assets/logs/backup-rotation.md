# Backup Rotation Log (Sanitized)

Timestamped extract from Proxmox Backup Server job history. Identifiers, domains, and IPs are sanitized.

```
2025-02-12T02:00:05Z INFO  job=vm/110 status=starting target=homelab-backups retention=7d/4w/12m
2025-02-12T02:00:07Z INFO  vm=wikijs-prod snapshot=auto before=38.2GB after=39.0GB dedupe=8.4% duration=132s
2025-02-12T02:02:30Z INFO  verify=success chunk-checks=1280 bandwidth=210MiB/s

2025-02-12T02:15:10Z INFO  job=vm/120 status=starting target=homelab-backups retention=7d/4w/12m
2025-02-12T02:15:12Z WARN  vm=homeassistant-prod note="qemu-guest-agent offline; using ACPI shutdown" action=force-stop
2025-02-12T02:17:55Z INFO  vm=homeassistant-prod snapshot=auto size=26.4GB dedupe=11.2% duration=163s
2025-02-12T02:18:12Z INFO  verify=success chunk-checks=910 bandwidth=185MiB/s

2025-02-12T02:30:03Z INFO  job=vm/130 status=starting target=homelab-backups retention=7d/4w/12m
2025-02-12T02:32:48Z ERROR vm=immich-prod stage=backup code=ENOSPC detail="datastore usage 87% > 85% threshold" action="paused schedule"
2025-02-12T02:32:50Z INFO  remediation="added NFS extent from TrueNAS backup pool" free_space=1.2TB
2025-02-12T02:33:10Z INFO  job=vm/130 status=restarted target=homelab-backups retention=7d/4w/12m
2025-02-12T02:36:41Z INFO  vm=immich-prod snapshot=auto size=142GB dedupe=6.1% duration=211s

2025-02-12T02:45:04Z INFO  job=ct/200 status=starting target=homelab-backups retention=4w/12m note="monitoring stack"
2025-02-12T02:47:25Z INFO  ct=monitoring snapshot=auto size=4.3GB dedupe=22.5% duration=141s

2025-02-12T03:00:00Z INFO  replication target=offsite-nas.example.com path=/mnt/backup/homelab policy=weekly encryption=aes256
2025-02-12T03:45:00Z INFO  replication status=success transferred=188GB duration=45m43s bandwidth=68MiB/s
```

**Summary:** Success=4 · Warning=1 (guest agent offline) · Error=1 (datastore capacity threshold, auto-remediated) · Actions: expand datastore, schedule re-verify, prune old snapshots.
