# Observability Evidence (Prometheus / Grafana / Loki)

## Prometheus alert snapshot
```
ALERT node_high_cpu IF avg by(instance)(rate(node_cpu_seconds_total{mode!="idle"}[5m])) > 0.8
Labels: severity="warning", instance="hera", environment="homelab"
Status: INACTIVE (cleared 2024-05-10T03:10:00Z)
```

## Grafana dashboard extract
- Dashboard: `Homelab Infra Overview`
- Panels: Proxmox cluster load, PBS throughput, TrueNAS latency, Unifi client count
- Annotation: `deploy immich patch` at 2024-05-09T21:30Z

## Loki log lines (redacted)
```
{service="nginx-proxy", host="atlas"} 2024-05-10T01:14:02Z TLS handshake completed sni=services.example.local status=200
{service="home-assistant", host="hera"} 2024-05-10T01:21:44Z automation executed id=energy_sync duration=324ms
{service="wikijs", host="zeus"} 2024-05-10T01:24:11Z http_request path="/search" status=200 latency=142ms
```
