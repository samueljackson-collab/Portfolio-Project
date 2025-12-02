# PRJ-WEB-001 Assets (Commercial E-commerce & Booking Systems)

**Status:** 🔄 Recovery — sanitized artifacts published for review.

## Navigation
- [Project README](../README.md)
- [Recovery Log](../RECOVERY.md)
- [Runbooks](docs/runbooks/)
- [Case Studies](docs/case-studies/recovery-case-studies.md)
- [Code Samples](code/)
- [Diagrams](diagrams/architecture.md)
- [Screenshots Plan](screenshots/README.md)

## Contents
### 💻 code/
Sanitized excerpts demonstrating catalog safety controls and booking logic.
- SQL: [catalog_backup_catalog.sql](code/sql/catalog_backup_catalog.sql) (hash-tracked backup workflow), [catalog_import_validation.sql](code/sql/catalog_import_validation.sql) (pre-flight validation gate).
- PHP: [booking_rate_calculator.php](code/php/booking_rate_calculator.php) (normalized pricing calculator excerpt).

### 📝 docs/
- Runbooks: [deployment pipeline](docs/runbooks/deployment_pipeline.md) and [content/catalog ops](docs/runbooks/content_ops.md).
- Case Studies: [recovery-case-studies.md](docs/case-studies/recovery-case-studies.md) summarizing issue → fix → outcome.

### 📊 diagrams/
- [architecture.md](diagrams/architecture.md) — Mermaid architecture + ERD highlights for catalog, booking, and ops domains.

### 📷 screenshots/
- [README](screenshots/README.md) documents sanitized capture scope and redaction steps; screenshots will be added post-validation.

## Security & Privacy
- All examples use placeholder SKUs, domains, and promo codes.
- Backups referenced are sanitized and hash-documented before analysis.
- Follow anonymization checklist in [RECOVERY.md](../RECOVERY.md#anonymization-checklist) before adding new assets.
