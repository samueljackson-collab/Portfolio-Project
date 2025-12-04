# Architecture

## Logical View
- **Event Producer**: Generates roaming attach/registration/session events with configurable profiles (urban, rural, cross-border).
- **Network Impairment Injector**: Adds latency/jitter/packet-loss per carrier link to mimic congestion and packet drops.
- **Roaming Policy Engine**: Applies steering rules, fair-use policies, and fraud heuristics before forwarding to consumers.
- **Event Consumer**: Parses events into KPIs and exports JSONL for downstream analytics.
- **Observability**: Prometheus scrape targets on producer/consumer and Loki for ingesting simulator logs.

```
[UE Trace] -> [Producer] -> [Policy Engine] -> [Consumer] -> [Metrics + Logs]
                             |                     |
                             v                     v
                       [Impairment]         [QoS Alerts]
```

## Deployment Topology
- **Local/Compose**: Single-node stack with dedicated containers for producer, consumer, and impairment service.
- **Kubernetes**: Uses kustomize overlays (`k8s/base`, `k8s/overlays/dev|stage|prod`) with horizontal pod autoscaling for producer throughput.
- **Data Paths**: Events flow over gRPC on port 50051; metrics exposed on 9100/9200; logs shipped to Loki via promtail sidecar.

## Data Model
- Event schema fields: `event_id`, `timestamp`, `imsi`, `msisdn`, `home_plmn`, `visited_plmn`, `radio`, `latency_ms`, `loss_pct`, `throughput_mbps`, `policy_action`.
- KPIs derived: attach success rate, average handover latency, fraud-rule hit rate, drop-call percentage.

## Security & Compliance
- Mutual TLS between producer and consumer using certs mounted via Kubernetes secrets.
- PII minimization by hashing IMSI/MSISDN in logs; raw values only kept in encrypted volumes.
- Audit trail via signed event batches stored in object storage (stubbed in this pack with local artifacts).
