# Monitoring Evidence (Prometheus/Grafana/Loki)

## Prometheus Scrape Summary
```
job="unifi-metrics" up{instance="controller.local:9100"} 1
job="proxmox-node"  scrape_duration_seconds 0.243  # sanitized hostnames
job="pfsense-firewall" scrape_samples_post_metric_relabeling 512
```

## Grafana Dashboard Snapshot
- Panels: WAN throughput, VPN peers, AP channel utilization
- Time range: last 24h (rolling)
- Alerts: `wan_loss` and `latency_slo_breach` both **OK** at capture time

## Loki Log Excerpts (sanitized)
```
{app="pfsense"} 2024-05-10T02:14:22Z allow vlan20->wan bytes=23140
{app="unifi"}   2024-05-10T02:16:09Z client_roam ap=office-ap01 rssi=68
{app="proxmox"} 2024-05-10T02:21:51Z vm=home-assistant snapshot=delta size=92MiB
```

All entries have been redacted to remove tenant names, MAC addresses, and public IPs.
