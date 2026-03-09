# Monitoring Evidence (Sanitized)

## Prometheus Alertmanager (excerpt)
```
- alert: VLANDropSpikes
  expr: rate(firewall_blocked_packets_total[5m]) > 25
  labels:
    severity: warning
    vlan: dmz
  annotations:
    summary: "DMZ drop rate exceeded 25 pps"
    description: "pfSense firewall blocking excessive connections on VLAN50"
```

## Grafana Dashboard JSON (snippet)
```
{
  "title": "VLAN Health",
  "panels": [
    {
      "title": "Latency by VLAN",
      "type": "timeseries",
      "targets": [
        {"expr": "histogram_quantile(0.95, rate(vlan_latency_seconds_bucket{vlan=\"servers\"}[5m]))"},
        {"expr": "histogram_quantile(0.95, rate(vlan_latency_seconds_bucket{vlan=\"iot\"}[5m]))"}
      ]
    }
  ]
}
```

## Loki Log Sample
```
2024-12-18T03:11:08Z vlan=guest app=unifi-firewall action=allow src=192.168.30.24 dst=1.1.1.1:443 proto=tcp bytes=1532 msg="Guest web egress"
2024-12-18T03:11:11Z vlan=dmz app=nginx-proxy action=allow src=192.168.50.12 dst=10.0.0.5:80 proto=tcp bytes=3829 msg="Reverse proxy health-check"
2024-12-18T03:12:45Z vlan=trusted app=proxmox action=allow src=192.168.10.5 dst=192.168.40.11:8006 proto=tcp bytes=2401 msg="Admin session"
```

All entries scrubbed of hostnames, public IPs, and user identifiers. Use these as references during audits without exposing sensitive data.
