# Lessons Learned & Anonymization Checks

## Recovery Lessons
- **Backups need labels and logs:** Every artifact now has a hash, storage location, and validation note.
- **Diagrams are part of the build:** ERD/architecture diagrams are rebuilt alongside code to prevent drift.
- **Runbooks must be testable:** Each procedure includes verification steps and rollback paths exercised in staging.
- **Guardrails before go-live:** Delta thresholds, duplicate detection, and negative-price checks block bad imports early.
- **Content needs observability:** Import logs and booking audit trails tie changes to operators and timestamps.

## Anonymization Checklist (apply before publishing)
- [ ] Replace domains with `example.com` and generic email addresses.
- [ ] Strip customer/order PII; keep only randomized sample data.
- [ ] Redact API keys, webhook URLs, gateway IDs, analytics tags, and license keys.
- [ ] Rename products/rooms/tours to neutral identifiers (e.g., `SKU-12345`, `ROOM-DELUXE`).
- [ ] Remove EXIF data and blur identifying text in screenshots.
- [ ] Confirm SQL/PHP snippets contain no client business logic or proprietary rates.
- [ ] Run `rg -n "http://|@|key|secret" assets` to spot potential leaks.

## Publication Controls
- Commit only sanitized outputs; keep raw backups offline.
- Maintain PR checklist: hashes recorded, snippets linted, links validated, README updated.
- Re-review case studies to ensure metrics are aggregate/relative, not exact client figures.
