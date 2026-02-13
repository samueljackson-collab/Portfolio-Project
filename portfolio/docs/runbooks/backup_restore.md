# Backup & Restore Procedures

## Services Covered
- PostgreSQL database
- Prometheus TSDB
- Grafana dashboards and configuration

## Backup Steps
1. Ensure Compose stack is running (`make up`).
2. Execute `scripts/backup.sh` (stub) or run manual commands:
   ```bash
   docker exec portfolio-postgres pg_dump -U postgres app > data/backups/postgres-$(date +%F).sql
   ```
3. Archive Grafana provisioning directory and Loki chunks to `data/backups/`.
4. Verify backup integrity with checksum (`shasum -a 256`).

## Restore Steps
1. Stop dependent services (`make down`).
2. Launch database only: `docker compose up postgres`.
3. Import SQL dump:
   ```bash
   cat data/backups/postgres-<DATE>.sql | docker exec -i portfolio-postgres psql -U postgres app
   ```
4. Restore Grafana dashboards by copying files into the provisioning directory and restarting the container.
5. Restart entire stack with `make up` and run smoke tests (`scripts/k6-smoke.js`).

