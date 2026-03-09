# Usage Examples

## Backup & Verify

```bash
./scripts/backup/pg_backup.sh
./scripts/backup/verify_backup.sh
```

## Restore

```bash
./scripts/backup/restore.sh backups/pg_backup_2024-01-01.dump target_db
```

## Upload to S3

```bash
./scripts/backup/s3_backup.sh backups/pg_backup_2024-01-01.dump
```

## Run Monitoring Queries

```bash
psql -f scripts/monitoring/query_performance.sql
psql -f scripts/monitoring/replication_lag.sql
```

## Maintenance

```bash
./scripts/maintenance/vacuum.sh
./scripts/maintenance/reindex.sh --database app_db
```

## Explain Plan Analysis

```bash
psql -d app_db -c "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM users WHERE id = 42" > explain.json
python3 scripts/performance/explain_analyzer.py explain.json
```

## Schema Migration

```bash
python3 scripts/migration/migrate.py
```

