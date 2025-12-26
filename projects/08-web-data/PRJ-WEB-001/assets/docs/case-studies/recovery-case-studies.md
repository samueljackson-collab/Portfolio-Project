# Recovery Case Studies (Sanitized)

## Case Study 1: Flooring Catalog Price Drift
**Problem:** Weekly supplier feeds introduced duplicate SKUs and double-counted price increases, causing mismatched cart totals.

**Action:**
- Rebuilt validation gate using [catalog_import_validation.sql](../../code/sql/catalog_import_validation.sql).
- Added SHA256-backed backup step before imports and enforced dry-run job recording in `ops_jobs`.

**Result:** Blocked 3 malformed imports during recovery drills; ensured <1% price delta variance after promotion.

## Case Study 2: Booking Calendar Overbooking
**Problem:** Inconsistent availability cache led to overlapping reservations during peak season.

**Action:**
- Refactored booking rate calculation to normalize occupancy logic ([booking_rate_calculator.php](../../code/php/booking_rate_calculator.php)).
- Added cache invalidation step in [content_ops.md](../runbooks/content_ops.md) whenever `booking_units` change.

**Result:** Eliminated double-booking incidents in test harness; checkout flow regained expected capacity validation.

## Case Study 3: Deployment Regression on Payment Plugin
**Problem:** Plugin update introduced API timeout; checkout failures spiked to 12%.

**Action:**
- Codified rollback and CDN/cache purge in [deployment_pipeline.md](../runbooks/deployment_pipeline.md).
- Captured screenshots and logs for regression evidence; maintained feature toggle to revert payment gateway.

**Result:** Mean checkout success returned to >70% within 30 minutes of rollback; validated safer release guardrails.
