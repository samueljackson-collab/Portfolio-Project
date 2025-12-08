# PRJ-WEB-001 Recovery Log

## Phase Summary
- **Backups Cataloged:** Located cold-storage SQL exports and week-over-week catalog snapshots; mapped each archive to anonymized environment names (prod, staging, dev) and checksum-tracked them for integrity verification.
- **Schema & ERD Reconstruction:** Rebuilt relational model (products, bookings, pricing rules, inventory, and audit tables) and captured the flows for catalog ingestion, bookings, and reporting.
- **Process Rebuild:** Recreated deployment, content operations, and monitoring runbooks with pre-flight checks, rollback steps, and validation queries.
- **Artifacts Published:** Sanitized SQL/PHP excerpts, architecture diagram (Mermaid), operational runbooks, case studies, and screenshot plan placed in the assets tree for reviewer access.
- **Governance:** Added anonymization checklist and lessons learned to prevent recurrence and guide future recoveries.

## Backup Catalog
| Source | Contents | Integrity | Notes |
|--------|----------|-----------|-------|
| `backups/sql/catalog-export-2023-11-12.sql.gz` | Product + taxonomy data (pricing, attributes, stock) | SHA256 recorded, decompressed successfully | Used to rebuild base catalog and price tables.
| `backups/sql/booking-ledger-2024-02-02.sql.gz` | Booking/reservation history with payment tokens removed | SHA256 recorded, schema-only import for ERD | Sanitized to drop PII fields before analysis.
| `backups/sql/cms-config-2024-03-20.sql.gz` | WordPress config, plugin settings, feature flags | SHA256 recorded, parsed via mysqldump headers | Informs environment toggles and content workflows.
| `backups/files/uploads-structure.tar.gz` | Media directory tree (filenames only) | SHA256 recorded, file list only | Used to re-create media references without binary payloads.

## Schema & ERD Highlights
See [assets/diagrams/architecture.md](assets/diagrams/architecture.md) for the reconstructed architecture and ERD overlays.
- **Products Domain:** `catalog_products` (SKUs, variations) links to `catalog_prices` (seasonal rates), `catalog_inventory` (stock), and `catalog_media` (asset references).
- **Bookings Domain:** `booking_reservations` connects customers to `booking_units` (rooms/tour slots) and `booking_rate_rules` (seasonal/occupancy pricing) with audit trails in `booking_events`.
- **Content/SEO Domain:** `content_pages`, `content_templates`, and `content_redirects` capture structured content and URL hygiene.
- **Operational Tables:** `ops_jobs` logs imports, while `ops_validations` tracks pre-/post-run checks for catalog loads.

## Workflow Documentation
- **Deployment Pipeline:** [assets/docs/runbooks/deployment_pipeline.md](assets/docs/runbooks/deployment_pipeline.md) codifies staging cutovers, DB backups, cache/CDN handling, and rollbacks.
- **Content Operations:** [assets/docs/runbooks/content_ops.md](assets/docs/runbooks/content_ops.md) covers catalog imports, SEO-safe edits, and weekly validation queries.
- **Monitoring & Run State:** [RUNBOOK.md](RUNBOOK.md) retains operational checks (SLOs, dashboards, alerting, health probes) and now references recovery-safe procedures.

## Published Artifacts
- **Sanitized Code:**
  - SQL catalog workflow: [assets/code/sql/catalog_backup_catalog.sql](assets/code/sql/catalog_backup_catalog.sql)
  - Validation queries: [assets/code/sql/catalog_import_validation.sql](assets/code/sql/catalog_import_validation.sql)
  - PHP booking logic excerpt: [assets/code/php/booking_rate_calculator.php](assets/code/php/booking_rate_calculator.php)
- **Architecture & ERD:** [assets/diagrams/architecture.md](assets/diagrams/architecture.md)
- **Runbooks:** Deployment and content operations under [assets/docs/runbooks/](assets/docs/runbooks/), with production ops in [RUNBOOK.md](RUNBOOK.md).
- **Case Studies:** Recovery narratives and before/after impacts in [assets/docs/case-studies/recovery-case-studies.md](assets/docs/case-studies/recovery-case-studies.md).
- **Screenshots:** Sanitized capture plan in [assets/screenshots/README.md](assets/screenshots/README.md); images will land in the same folder as recovered.

## Lessons Learned
1. **Backups with Integrity:** Store hashes alongside exports and test restores monthly; never keep only workstation copies.
2. **Schema-as-Code:** Keep ERDs and migration notes under version control to accelerate rebuilds.
3. **Runbooks per Workflow:** Every recurring content or deployment step now has a validated playbook with rollback hooks.
4. **Privacy by Default:** All examples scrub PII, replace domains, and drop payment tokens before analysis.

## Anonymization Checklist
- Strip client names, domains, email addresses, and phone numbers.
- Replace real SKUs, product names, and locations with neutral placeholders.
- Remove payment gateway tokens and transaction IDs.
- Redact media filenames that include client identifiers; prefer generic naming.
- Review code comments for hidden references; rephrase to neutral terminology.

## Recovery Timeline
| Date | Event | Outcome |
|------|-------|---------|
| 2025-11-10 | Cataloged backup archives and recorded hashes | ✅ Verified decompression and import headers |
| 2025-11-11 | Reconstructed schema/ERD from exports and notes | ✅ Mapped core domains and relationships |
| 2025-11-12 | Rebuilt deployment/content runbooks from memory and logs | ✅ Added rollback and validation steps |
| 2025-11-13 | Published sanitized code excerpts, diagrams, and case studies | ✅ Linked assets and updated portfolio README |

**Last Updated:** 2025-11-13
