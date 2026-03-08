---
title: Troubleshooting
description: - Validate `pg_dump` is installed and credentials are correct. - Check filesystem permissions for `BACKUP_DIR`. - Run `sql/monitoring/query_performance.sql` to identify expensive queries. - Use `scrip
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/troubleshooting
created: 2026-03-08T22:19:13.784072+00:00
updated: 2026-03-08T22:04:37.928902+00:00
---

# Troubleshooting

## Backup failures
- Validate `pg_dump` is installed and credentials are correct.
- Check filesystem permissions for `BACKUP_DIR`.

## Slow queries
- Run `sql/monitoring/query_performance.sql` to identify expensive queries.
- Use `scripts/performance/explain_analyze.sh` to inspect a query plan.

## Replication lag
- Run `sql/monitoring/replication_lag.sql` and confirm network throughput.
