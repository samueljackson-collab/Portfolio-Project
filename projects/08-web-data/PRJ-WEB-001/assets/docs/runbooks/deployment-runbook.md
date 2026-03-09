# Deployment Runbook — PRJ-WEB-001

Step-by-step guide to deploy sanitized WordPress/WooCommerce builds recovered for the portfolio. All domains and credentials are placeholders.

## Preconditions
- Git repo sanitized and tagged (e.g., `v1.0.0-sanitized`).
- `.env` populated with placeholder database credentials and `SITE_URL=https://example.com`.
- Maintenance page available (`maintenance.html`) for brief switchover.

## Pipeline Overview
1. **Backup:** `wp db export backups/pre-deploy-$(date +%F).sql` and snapshot `/var/www/html/wp-content/uploads`.
2. **Build:** Run `npm run build` for theme assets; package custom plugins (`zip -r build/plugins/*.zip`).
3. **Stage:** Deploy to staging container; run smoke tests and lint PHP (`php -l`) and SQL migration scripts.
4. **Maintenance toggle:** Enable maintenance mode (`wp maintenance-mode activate`).
5. **Deploy:**
   - Sync plugins/themes: `wp plugin install build/plugins/custom.zip --force`.
   - Apply DB migrations: `wp db import builds/migrations.sql` (sanitized).
   - Run composer installs if applicable.
6. **Post-deploy checks:**
   - `wp core verify-checksums`
   - `wp plugin list --status=active`
   - `curl -I https://example.com | grep 200`
   - `wp cron event list | head -10`
7. **Maintenance off:** `wp maintenance-mode deactivate`.
8. **Verification:** Browse key paths, check logs, and validate cache/CDN purge.

## Rollback
1. Activate maintenance mode.
2. Restore latest DB export: `wp db import backups/pre-deploy-YYYY-MM-DD.sql`.
3. Restore uploads snapshot; redeploy last-known-good plugin/theme packages.
4. Clear caches (`wp cache flush`, Redis flush if used) and purge CDN.
5. Disable maintenance and retest critical flows.

## Health Checks
- **Database connectivity:** `wp db check`
- **Cron status:** `wp cron event list --due-now`
- **Queue health (if using Action Scheduler):** `wp action-scheduler run --force`
- **Error budget:** Review last 200 lines of `wp-content/debug.log` for fatal errors.

## Notes
- Keep deployments under 15 minutes; longer requires business approval.
- All commands assume non-root `www-data` user in production; adjust with `sudo -u www-data`.
- Replace any remaining client references before commit; run anonymization checklist prior to tagging.
