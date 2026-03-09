# Content & Catalog Operations Runbook — PRJ-WEB-001

Guidelines for safely updating catalog data, bookings, and content during recovery. All data shown is synthetic.

## Catalog Import (High-SKU Store)
1. **Prep file:** Validate CSV headers match `SKU,Name,Price,Stock,Category,Image`. Normalize currency and units.
2. **Checksum:** `sha256sum import.csv > checksums/import.csv.sha256` and log in import job.
3. **Stage:** `LOAD DATA INFILE 'import.csv' INTO TABLE import_products_staging FIELDS TERMINATED BY ',' IGNORE 1 ROWS;`
4. **Validate:**
   - `SELECT COUNT(*) FROM import_products_staging WHERE price <= 0;`
   - `SELECT sku FROM import_products_staging GROUP BY sku HAVING COUNT(*) > 1;`
5. **Upsert:** Run sanitized SQL from `assets/code/sql/catalog_price_update.sql` to merge into `wp_posts`/`wp_postmeta`.
6. **Review:** Export delta report (insert/update/delete counts) and share for approval.
7. **Publish:** Promote to production tables, warm cache (`wp cache flush` + category prefetch), and purge CDN for changed categories.

## Price Update (Resort/Tour Booking)
1. Pull sanitized rate sheet; map to `WP_PRODUCT_PRICING` with `season_start`, `season_end`, `channel_price`.
2. Execute guardrail query: `SELECT sku, channel_price FROM WP_PRODUCT_PRICING WHERE channel_price NOT BETWEEN 25 AND 1500;`
3. Recalculate derived totals and taxes in staging; compare against prior snapshot.
4. Promote after approvals; archive rate sheet and update `WP_IMPORT_LOGS` with row counts/duration.

## Booking Calendar Adjustments
1. Create blackout dates in `WP_BOOKABLE_ITEMS` for maintenance or full buy-outs.
2. Run availability check script (`assets/code/php/booking_availability_example.php`) to verify overlap logic.
3. Force-refresh cached availability endpoints and confirm ICS feed updates.
4. Document change in `WP_BOOKING_META` with reason and operator initials.

## Content Changes (Pages/Posts)
1. Draft in staging; run `wp post list --post_type=page --format=ids` to capture changed IDs.
2. Execute visual review and accessibility spot-check (headings, alt text, contrast) on changed pages.
3. Deploy via standard pipeline; purge CDN for modified slugs.
4. Capture before/after screenshots (sanitized) and store in `assets/screenshots/` with blur applied.

## Troubleshooting Quick Hits
- **Import fails:** Check CSV encoding (UTF-8), line endings, and file size; rerun with `--local-infile` enabled.
- **Cache stale:** `wp cache flush` + Redis flush + CDN purge for affected paths.
- **Availability mismatch:** Rebuild booking cache and ensure timezones are consistent (UTC for DB, local for display).
- **Plugin regression:** Disable suspect plugin via CLI (`wp plugin deactivate <name>`) and retest baseline checkout/booking.

## Controls & Approvals
- All imports require checksum + row-count validation and approval from content owner.
- No PII permitted in staging data; synthetic samples only.
- Maintain audit trail in `WP_IMPORT_LOGS` and `RECOVERY_TIMELINE.md` for each change.
