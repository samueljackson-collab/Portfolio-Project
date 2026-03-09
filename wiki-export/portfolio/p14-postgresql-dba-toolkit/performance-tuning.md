---
title: Performance Tuning Guide
description: - Ensure `shared_buffers`, `work_mem`, `maintenance_work_mem` are sized for the workload. - Review sequential scan hot spots using `sql/performance/index_suggestions.sql`. - Use `scripts/performance/e
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/performance-tuning
created: 2026-03-08T22:19:13.781053+00:00
updated: 2026-03-08T22:04:37.927902+00:00
---

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
