# Recovery Timeline — PRJ-WEB-001

Chronological log of recovery actions, artifacts, and verification checks. Dates are relative to the current rebuild window.

## Week 1 — Catalog & Backup Validation
- **Day 1:** Located cold-storage archives and S3 snapshot exports; documented storage locations and hashes.
- **Day 2:** Validated SQL dumps with checksum + dry-run imports into disposable Dockerized MySQL.
- **Day 3:** Extracted anonymized sample data and produced sanitized price-update SQL script.
- **Day 4:** Reconstructed ERD from schema diff plus WordPress/WooCommerce defaults; added booking and inventory tables.
- **Day 5:** Drafted backup catalog and anonymization checklist; logged verification steps in runbook.

## Week 2 — Process & Runbook Reconstruction
- **Day 6:** Rebuilt deployment workflow (Git → build → stage → backup → maintenance → deploy → post-checks).
- **Day 7:** Recreated content operations runbook covering catalog imports, price updates, and booking calendar edits.
- **Day 8:** Captured workflow diagrams for catalog → pricing → publishing and booking pipeline.
- **Day 9:** Wrote sanitized PHP availability checker snippet and WordPress CLI deployment checks.
- **Day 10:** Created case study for catalog recovery and mapped SLOs to monitoring hooks.

## Week 3 — Publication & Review
- **Day 11:** Generated architecture and ERD diagrams (Mermaid) with labels anonymized.
- **Day 12:** Published sanitized screenshots index and documentation links; cross-referenced in README.
- **Day 13:** Reviewed lessons learned, anonymization guardrails, and rollback controls.
- **Day 14:** Final QA pass: link validation, spell check, and repository README updates.

## Confidence & Outstanding Items
- **Confidence:** Medium-high for schema fidelity; medium for plugin-level behavior (more snippets planned).
- **Outstanding:** Add redacted performance dashboards, payment gateway sandbox replay steps, and CDN purge script examples.
