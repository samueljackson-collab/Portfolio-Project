# Connection Pool Tuning

## PgBouncer Sizing
- Start with pool size equal to 2-4x CPU cores.
- Use transaction pooling for high-throughput APIs.
- Keep `max_client_conn` aligned to application fan-out.

## When to Scale
- If `active` connections are consistently > 80% of max.
- If average wait time for a connection > 200ms.

## Monitoring Signals
- `pg_stat_activity` active/idle count.
- PgBouncer `SHOW POOLS` for wait counts.
