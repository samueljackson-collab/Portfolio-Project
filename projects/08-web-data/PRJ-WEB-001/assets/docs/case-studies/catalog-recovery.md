# Case Study — Catalog Recovery & Price Automation

## Context
A flooring store with 10,000+ SKUs relied on weekly CSV uploads and ad-hoc price changes. The original automation scripts were lost with a retired workstation, leaving only partial SQL dumps and memory of workflows.

## Problem
- Price updates were manual and error-prone after data loss.
- No visibility into which SKUs changed each week.
- Cache/CDN mismatches caused stale pricing on product detail pages.

## Approach
1. **Backup cataloging:** Indexed all available dumps/exports with hashes and staged them in disposable MySQL for integrity checks.
2. **Schema reconstruction:** Rebuilt ERD and staging tables to match WooCommerce plus custom pricing extensions.
3. **Script recreation:** Authored sanitized SQL upsert (`catalog_price_update.sql`) to merge staged data with live catalog tables.
4. **Workflow hardening:** Added guardrails (delta thresholds, negative price detection) and automated CDN/cache purges post-publish.
5. **Observability:** Logged every import in `WP_IMPORT_LOGS` with source, duration, row counts, and anomalies.

## Outcome
- **Time saved:** Weekly updates reduced from ~2 hours manual edits to ~15 minutes with automated upsert + validation.
- **Error reduction:** Negative/zero-price defects eliminated via guardrail queries; duplicate SKUs blocked at staging.
- **Confidence:** Backups cataloged with hashes; dry-run imports prevent production corruption.

## Artifacts
- [Backup catalog](../recovery-backup-catalog.md)
- [Schema & ERD](../schema-and-erd.md)
- [Sanitized SQL upsert](../../code/sql/catalog_price_update.sql)
- [Content operations runbook](../runbooks/content-operations-runbook.md)

## Lessons Learned
- Treat staging as production for data hygiene; enforce constraints before promoting.
- Keep per-import audit logs to support rollbacks and stakeholder comms.
- Pair CDN purges with cache warms to avoid cold-start penalties after bulk updates.
