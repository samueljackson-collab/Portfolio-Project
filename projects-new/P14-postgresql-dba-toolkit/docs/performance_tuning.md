# Performance Tuning Guide

## Quick Wins
- Ensure `shared_buffers`, `work_mem`, `maintenance_work_mem` are sized for the workload.
- Review sequential scan hot spots using `sql/performance/index_suggestions.sql`.

## Query Analysis
- Use `scripts/performance/explain_analyze.sh` for target queries.
- Review `sql/monitoring/query_performance.sql` for top queries.

## Connection Pooling
- Compare `max_connections` to connection pool size.
- Use `sql/performance/pool_tuning.sql` for guidance.
