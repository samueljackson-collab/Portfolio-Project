# Deployment Pipeline Runbook (Sanitized)

## Overview
Recreated deployment workflow for WordPress/WooCommerce stacks supporting catalog-heavy stores and booking sites. Applies to staging → production promotions with rollback readiness.

## Pre-Deployment Checklist
- [ ] Confirm latest backups: database dump (`wp db export`), `wp-content` tarball, and `.env` snapshot with secrets removed from commit history.
- [ ] Validate schema drift: compare `INFORMATION_SCHEMA` checksums between staging and prod; block deploy if drift detected.
- [ ] Review plugin/theme update list with change impact notes; obtain approvals for payment/shipping integrations.
- [ ] Clear maintenance window and stakeholder comms (status page + email template).

## Staging Validation
1. Pull release branch and install dependencies (`composer install`, `npm ci` if theme build exists).
2. Run database migrations or import sanitized data seed.
3. Execute smoke tests:
   - `/healthz` endpoint returns 200.
   - Sample product page TTFB < 800ms.
   - Checkout sandbox flow completes with test token.
4. Capture before/after screenshots for key pages (home, category, checkout) for regression evidence.

## Promotion Steps
1. **Freeze writes** (enable WooCommerce maintenance mode) to prevent cart drift.
2. **Backup production DB** and `wp-content` to `backups/prod/YYYYMMDD-HHMM/` with SHA256 manifest.
3. **Deploy code**
   - Sync theme/plugin updates (`rsync` or CI artifact) to `/var/www/html/wp-content`.
   - Reload PHP-FPM and web server.
4. **Database updates**
   - Apply migrations or run `wp db import` for sanitized data patches.
   - Execute [catalog validation queries](../../code/sql/catalog_import_validation.sql) against production with read-only creds.
5. **Cache & CDN**
   - Warm Redis object cache (`wp cache flush` then prime critical pages).
   - Purge CDN paths for updated assets (`/wp-content/themes/*`, `/wp-content/uploads/*`).
6. **Feature toggles**
   - Toggle new features via options table/config flags; keep rollback toggles documented.

## Post-Deployment Validation
- Confirm uptime and log absence of PHP fatal errors for 15 minutes.
- Run synthetic checkout and booking flow with test user to validate payment + availability lookups.
- Review Grafana panels: error rate < 1%, p95 TTFB < 900ms, DB query time < 200ms.
- Verify search index or caching jobs rehydrated (if applicable).

## Rollback Plan
- Re-enable maintenance mode.
- Restore latest DB + `wp-content` backups from `backups/prod/*`.
- Revert to previous artifact build (Git tag `release-prev`).
- Purge caches and CDN; re-run smoke tests.

## Evidence to Capture
- Deployment command log (timestamps, operator).
- Hash manifest for backups and deployed artifacts.
- Screenshots: homepage, category page, product detail, booking/calendar page, checkout success.

## Notes
- All paths, domains, and identifiers are placeholders to avoid client disclosure.
