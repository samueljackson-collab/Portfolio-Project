# P13 – High-Availability Web App

A two-tier web app served via NGINX load balancer with replicated application containers and PostgreSQL HA via Patroni. Designed to demonstrate zero-downtime deployments and automated failover.

## Quick start
1. Launch stack: `docker compose up -d` to start NGINX, app nodes, and Patroni cluster.
2. Seed database: `make db-seed` loads baseline fixtures and health checks replication slots.
3. Run synthetic tests: `k6 run tests/synthetic.js --vus 20 --duration 2m`.
4. Simulate failover: `scripts/trigger_failover.sh` then confirm NGINX upstream health.

## Components
- `compose.yaml`: NGINX, app replicas, Patroni/postgres nodes.
- `nginx/conf.d/`: upstream definitions with passive health checks.
- `scripts/failover_validation.sh`: verifies read/write path during primary swap.
