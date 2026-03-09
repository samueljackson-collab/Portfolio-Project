---
title: Performance Tuning Guide
description: - CPU utilization - Memory usage and cache hit ratio - I/O latency and throughput - Query latency (p95/p99) - `shared_buffers`: 25-40% of system RAM for dedicated DB hosts. - `work_mem`: Tune based on
tags: [analytics, data-engineering, documentation, pipeline, portfolio]
path: portfolio/2-database-migration/performance-tuning-guide
created: 2026-03-08T22:19:13.255972+00:00
updated: 2026-03-08T22:04:38.597902+00:00
---

# Performance Tuning Guide

## Baseline Metrics
- CPU utilization
- Memory usage and cache hit ratio
- I/O latency and throughput
- Query latency (p95/p99)

## Configuration Focus Areas

### Memory
- `shared_buffers`: 25-40% of system RAM for dedicated DB hosts.
- `work_mem`: Tune based on concurrent query load.
- `maintenance_work_mem`: Increase for vacuum and index creation.

### WAL & Checkpoints
- Increase `max_wal_size` to reduce checkpoint frequency.
- Tune `checkpoint_completion_target` to smooth writes.

### Autovacuum
- Adjust `autovacuum_vacuum_scale_factor` for large tables.
- Monitor `pg_stat_user_tables` for dead tuple growth.

## Index Strategy
- Use `scripts/performance/index_suggestion.sql` to find candidate indexes.
- Drop unused indexes reported in `scripts/monitoring/index_usage.sql`.
- Consider partial or covering indexes for high-frequency queries.

## Query Optimization
- Normalize slow queries and avoid nested loops on large datasets.
- Use `EXPLAIN (ANALYZE, BUFFERS)` to identify hotspots.
- Partition large tables when it improves query pruning.

## Connection Pooling
- Deploy PgBouncer for high concurrency.
- Size pool based on CPU cores and workload type.

