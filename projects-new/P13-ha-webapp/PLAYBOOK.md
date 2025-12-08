# Operations Playbook

## Deployments
- Local: `docker compose pull && docker compose up -d --build`.
- Rolling update: take one app container out of rotation `docker compose stop app1`, upgrade image, then swap.
- Database patch: apply migrations via `make migrate` with Patroni maintenance window enabled.

## Operations
- Monitor `/_health` from each app and Patroni `/patroni` endpoints; alerts fire when replication lag > 5s.
- Rotate TLS certs using `scripts/rotate_certs.sh` and reload NGINX `docker compose exec nginx nginx -s reload`.

## Validation
- `scripts/failover_validation.sh` after any DB change.
- `scripts/cache_warm.sh` to repopulate application caches post-deploy.
