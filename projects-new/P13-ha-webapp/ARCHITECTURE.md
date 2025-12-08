# Architecture

Traffic terminates at NGINX with SSL, then routes to two containerized app nodes. Patroni manages PostgreSQL primary/replica with etcd consensus. HAProxy health endpoints expose cluster status to NGINX for automatic upstream draining during failover.

## Flow
1. Requests hit `https://host` and are balanced across app containers.
2. App nodes read/write via Patroni VIP; WAL streaming keeps replicas current.
3. Metrics emitted to Prometheus exporters for NGINX and PostgreSQL; alerts fire for replication lag.

## Dependencies
- Docker Compose, NGINX 1.24+, PostgreSQL 15 with Patroni.
- `psycopg`, `gunicorn`, `prometheus-nginx-exporter`, `postgres_exporter`.
- TLS certs placed under `certs/` for local SSL.
