# Backup Catalog — PRJ-WEB-001

Catalog of available backups, verification steps, and anonymization controls used during recovery.

## Inventory

| Source | Location | Contents | Verification | Notes |
|--------|----------|----------|--------------|-------|
| Cold storage USB | Offline drive (label: `WEB-ARCHIVE-A`) | SQL dumps (`wp_posts`, `wp_postmeta`, `wp_terms`), media tarball | SHA256 hash + `mysql --force --one-database` dry-run | Mounted read-only; copies stored in encrypted vault |
| S3 snapshot | `s3://redacted-ecomm-backups/2021-09/` | Full WordPress export + WooCommerce products CSV | `aws s3 sync --dryrun` + `wp import --skip=authors` in staging | Accessed with temporary role; bucket names anonymized |
| Client handoff ZIP | Email archive | Theme/plugin ZIPs, child-theme overrides | ClamAV scan + unzip integrity + `php -l` lint | Sensitive logos removed prior to use |
| Local git snapshot | `~/archives/web-sanitized.git` | Sanitized plugin hooks, deployment scripts | `git fsck --full` + manual diff against vanilla plugins | Contains only anonymized identifiers |

## Verification Workflow

1. **Hash & lock:** Compute SHA256 for each artifact and store in `assets/docs/verification-log.txt` (not committed with secrets).
2. **Dry-run imports:** Use disposable Docker MySQL (`mysql:8`) to run `mysql --force < dump.sql` with `--set-gtid-purged=OFF` to detect corruption.
3. **Selective restore:** Import only structure and sample rows needed for ERD reconstruction (`--where` filters for generic SKUs/customers).
4. **Media scrub:** Remove EXIF and alt-text with brand terms using `exiftool -all=` and bulk rename to generic filenames.
5. **Credential purge:** Validate no secrets remain via `rg -n "api_key|password|secret"` on extracted trees.

## Retention & Access
- **Retention:** Backups kept 30 days post-publication, then rotated to encrypted cold storage.
- **Access:** Recovery artifacts stored in a private vault; only sanitized outputs are committed.
- **Logging:** Access timestamps recorded in local vault audit log; not stored in repo.

## Anonymization Gates
- Replace domains with `example.com` and emails with `user@example.com`.
- Map product/room/tour names to generic placeholders (e.g., `SKU-10001`, `ROOM-DELUXE`).
- Strip customer PII and order history; only synthetic data used in examples.
- Remove payment gateway IDs, API keys, webhook URLs, and GA/FB pixels.
- Ensure screenshots blur names, addresses, and booking IDs before publication.

## Rapid Checks (10-minute drill)
- `sha256sum *.sql *.csv *.zip` — confirm against catalog.
- `docker run --rm -v $PWD:/data mysql:8 mysqlcheck -uroot --all-databases --quick` — quick corruption scan.
- `php -l assets/code/php/*.php` — lint sanitized PHP snippets.
- `rg -n "<client>|companyname|http://" assets` — verify anonymization.
