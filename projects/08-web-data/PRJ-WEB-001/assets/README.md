# Commercial E-commerce & Booking Systems — Assets

**Status:** 🔄 Recovery (Phase 1 artifacts published)

## Description
Supporting materials for the recovery of legacy e-commerce and booking systems. All content is sanitized and client-agnostic.

## Links
- [Project README](../README.md)
- [Recovery Timeline](../RECOVERY_TIMELINE.md)
- [Backup Catalog](./docs/recovery-backup-catalog.md)
- [Schema & ERD](./docs/schema-and-erd.md)
- [Runbooks](./docs/runbooks)
- [Case Studies](./docs/case-studies)
- [Lessons & Anonymization](./docs/lessons-and-anonymization.md)
- [Sanitized Code](./code)
- [Screenshots](./screenshots)

## Directory Guide

### 💻 code/
Sanitized examples only:
- **sql/** — bulk import/upsert scripts (e.g., `catalog_price_update.sql`).
- **php/** — plugin excerpts and booking helpers (e.g., `booking_availability_example.php`).
- **scripts/** — auxiliary utilities (add future backup/check scripts here).

### 📊 docs/
- **recovery-backup-catalog.md** — backup inventory and verification steps.
- **schema-and-erd.md** — ERD diagram and data workflows.
- **runbooks/** — deployment and content operations runbooks.
- **case-studies/** — narratives (e.g., catalog recovery).
- **lessons-and-anonymization.md** — lessons learned and publication checklist.

### 📷 screenshots/
Sanitized image index and guidelines for preparing blurred/redacted assets.

## Security & Privacy Reminder
- Remove ALL client identifiers before adding files.
- Use synthetic data; never commit raw backups or credentials.
- Run the anonymization checklist before pushing updates.
