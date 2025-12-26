# Kubernetes Deployment for Real-time Data Streaming

## Overview

This directory contains Kubernetes manifests for deploying the complete streaming infrastructure including Kafka, Zookeeper, Schema Registry, and Flink.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Zookeeper   │  │    Kafka     │  │    Schema    │     │
│  │  StatefulSet │  │  StatefulSet │  │   Registry   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Flink        │  │  Producers/  │                        │
│  │ JobManager   │  │  Consumers   │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │     Flink TaskManager (replicas=3)        │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- 16GB+ RAM total across nodes
- Persistent volume provisioner

## Quick Start

```bash
# Create namespace
kubectl create namespace streaming

# Deploy in order
kubectl apply -f namespace.yaml
kubectl apply -f zookeeper/
kubectl apply -f kafka/
kubectl apply -f schema-registry/
kubectl apply -f flink/

# Verify deployments
kubectl get all -n streaming

# Check logs
kubectl logs -n streaming -l app=kafka
kubectl logs -n streaming -l app=flink-jobmanager
```

## Components

### Zookeeper
- **StatefulSet** with 3 replicas
- Persistent storage for coordination
- Headless service for peer discovery

### Kafka
- **StatefulSet** with 3 brokers
- Persistent storage per broker
- Internal and external access services
- Auto-create topics enabled

### Schema Registry
- **Deployment** with 2 replicas
- Connected to Kafka cluster
- REST API on port 8081

### Flink
- **JobManager**: Deployment with 1 replica
- **TaskManager**: Deployment with 3 replicas
- Configured for high availability
- RocksDB state backend
- Checkpointing enabled

## Configuration

### Resource Requests/Limits

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Zookeeper | 500m | 1Gi | 1 | 2Gi |
| Kafka | 1 | 2Gi | 2 | 4Gi |
| Schema Registry | 250m | 512Mi | 500m | 1Gi |
| Flink JobManager | 1 | 2Gi | 2 | 4Gi |
| Flink TaskManager | 2 | 4Gi | 4 | 8Gi |

### Storage

- **Zookeeper**: 10Gi per replica
- **Kafka**: 100Gi per broker
- **Flink**: 50Gi for checkpoints

## Networking

### Services

- **kafka-service**: Internal (ClusterIP) on 9092
- **kafka-external**: External (LoadBalancer) on 9094
- **schema-registry**: ClusterIP on 8081
- **flink-jobmanager**: ClusterIP on 8081 (Web UI), 6123 (RPC)
- **zookeeper**: Headless service for StatefulSet

### Ingress (Optional)

```yaml
# Expose Flink UI
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: flink-ui
  namespace: streaming
spec:
  rules:
  - host: flink.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: flink-jobmanager
            port:
              number: 8081
```

## Monitoring

### Prometheus Metrics

All components expose Prometheus metrics:

- **Kafka**: Port 9308 (JMX exporter)
- **Flink**: Port 9249
- **Schema Registry**: Port 8081/metrics

### Service Monitors

```bash
kubectl apply -f monitoring/service-monitors.yaml
```

## Scaling

### Scale Kafka Brokers

```bash
kubectl scale statefulset kafka -n streaming --replicas=5
```

### Scale Flink TaskManagers

```bash
kubectl scale deployment flink-taskmanager -n streaming --replicas=5
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n streaming -w
```

### View Logs

```bash
# Kafka logs
kubectl logs -n streaming kafka-0 -f

# Flink JobManager logs
kubectl logs -n streaming -l app=flink-jobmanager -f

# Schema Registry logs
kubectl logs -n streaming -l app=schema-registry -f
```

### Common Issues

**Pods stuck in Pending**:
- Check PVC status: `kubectl get pvc -n streaming`
- Verify node resources: `kubectl describe nodes`

**Kafka connection issues**:
- Verify Zookeeper is running
- Check Kafka logs for broker registration
- Test connectivity: `kubectl exec -it kafka-0 -n streaming -- kafka-topics.sh --bootstrap-server localhost:9092 --list`

**Flink jobs failing**:
- Check TaskManager logs
- Verify sufficient memory/CPU
- Review checkpoint storage access

## Cleanup

```bash
# Delete all resources
kubectl delete namespace streaming

# Delete PVCs (if needed)
kubectl delete pvc -n streaming --all
```

## Production Considerations

1. **High Availability**:
   - Run 3+ Kafka brokers
   - Enable Flink HA mode
   - Use anti-affinity for pod distribution

2. **Security**:
   - Enable TLS for Kafka
   - Configure SASL authentication
   - Use NetworkPolicies

3. **Backup**:
   - Snapshot Kafka volumes
   - Backup Zookeeper data
   - Export Flink checkpoints

4. **Monitoring**:
   - Set up Prometheus + Grafana
   - Configure alerts for broker down, lag, etc.
   - Monitor JVM metrics

5. **Tuning**:
   - Adjust heap sizes based on workload
   - Configure Kafka log retention
   - Tune Flink checkpoint intervals

## References

- [Kafka on Kubernetes](https://strimzi.io/)
- [Flink Kubernetes Operator](https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-stable/)
- [Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
