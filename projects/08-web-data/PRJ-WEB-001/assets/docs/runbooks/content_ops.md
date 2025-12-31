# Content & Catalog Operations Runbook (Sanitized)

## Weekly Catalog Refresh
1. **Extract** supplier CSV/Excel to staging and normalize headers to canonical schema (`sku`, `name`, `price`, `stock_qty`, `category_path`, `attributes_json`).
2. **Validate** using [catalog import validation](../../code/sql/catalog_import_validation.sql) against staging DB with read-only user.
3. **Load** via ETL script (scheduled cron) into `ops_jobs` with dry-run first; block if validation fails.
4. **Promote** to production during low-traffic window; re-run validation and regenerate price index.
5. **Publish** change log summarizing SKU deltas, price changes >10%, and stockouts.

## New Product Launch Flow
- Create record in `catalog_products` with generated SKU (`SKU-{CATEGORY}-{SEQ}`) and attach attributes.
- Upload media using sanitized filenames (`category-sku-angle-01.jpg`); avoid brand-specific strings.
- Build SEO template: H1, meta description, structured data block (Product schema), breadcrumbs path.
- Validate page speed in staging; ensure image compression < 300KB and lazy loading enabled.
- Schedule publication with CDN warmup for hero/category pages.

## Booking Content Updates
- Update `booking_rate_rules` for seasonal pricing; pair every change with `effective_from`/`effective_to` and audit note.
- Adjust availability in `booking_units` and trigger calendar cache invalidation.
- Send preview links to stakeholders; capture screenshots for records.

## Governance & Review
- Peer review all SQL changes and content templates prior to production promotion.
- Enforce anonymization: scrub client names, addresses, payment tokens, and traveler PII from any sample data.
- Maintain evidence: export validation query results and screenshot diffs into `assets/screenshots/`.

## Troubleshooting Playbook
- **Import fails validation:** inspect `ops_validations` rows; rerun ETL in dry-run mode with narrowed dataset.
- **Cache stale content:** purge CDN paths for affected categories; flush Redis object cache, then warm top 20 pages.
- **Unexpected price swings:** compare current `catalog_prices` to previous snapshot via delta query; rollback using backup manifest if needed.
