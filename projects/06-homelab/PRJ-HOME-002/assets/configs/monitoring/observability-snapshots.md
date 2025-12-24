# Observability Evidence (Prometheus/Grafana)

## Prometheus Recording Rule (excerpt)
```
- record: job:http_availability:ratio_rate5m
  expr: sum(rate(http_requests_total{status=~"2.."}[5m]))
        /
        sum(rate(http_requests_total[5m]))
  labels:
    service: reverse-proxy
```

## Grafana Panel (JSON snippet)
```
{
  "title": "Proxmox Cluster Health",
  "targets": [
    {"expr": "avg(proxmox_node_cpu_usage_percent{cluster='homelab'})"},
    {"expr": "avg(proxmox_node_memory_usage_percent{cluster='homelab'})"}
  ],
  "thresholds": [
    {"color": "#EAB839", "value": 75},
    {"color": "#C4162A", "value": 90}
  ]
}
```

## Loki Log Snippet (reverse proxy)
```
2024-12-18T04:21:41Z service=nginx-gateway ingress=ha status=200 path=/api/health latency_ms=24 client=192.168.40.12
2024-12-18T04:22:05Z service=nginx-gateway ingress=wikijs status=200 path=/ latency_ms=37 client=192.168.40.15

All entries scrubbed of DNS names and private identifiers.
