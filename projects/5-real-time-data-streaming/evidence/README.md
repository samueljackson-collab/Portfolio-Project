# Real-time Data Streaming Evidence

## Deployment Attempt

The Kubernetes deployment was attempted from this environment, but the required tooling and cluster access were not available.

### Command Output

```bash
$ kubectl version --client
bash: command not found: kubectl
```

## Metrics & Charts

Throughput, end-to-end latency percentiles, and error-rate metrics require a running Kubernetes stack with Prometheus/Grafana scraping the streaming services. Because the cluster tooling was unavailable in this environment, no Prometheus data or Grafana dashboards could be queried, and no charts/screenshots could be produced here.

### How to Generate Metrics Once a Cluster Is Available

1. Ensure `kubectl` is installed and configured for the target cluster.
2. Deploy the stack following `k8s/README.md`.
3. Run a sample workload from the project root (example):

```bash
python src/producer.py --high-volume --rate 100 --duration 60
```

4. Query Prometheus for throughput and latency metrics, then export charts (Grafana panels or Prometheus query results). Store resulting CSV/PNG outputs under this directory.
5. Capture dashboard screenshots from Grafana and save them alongside the charts.

