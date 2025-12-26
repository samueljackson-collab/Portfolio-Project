# Screenshots — PRJ-WEB-001

Sanitized screenshot index for the recovery effort. Actual images are anonymized and should mask any client identifiers.

## Included/Planned Shots
- **Catalog admin (sanitized):** Product list with neutral SKUs (`SKU-10001` etc.) and blurred branding.
- **Booking calendar (sanitized):** Availability grid showing synthetic dates and capacities.
- **Price update report:** Delta summary before/after bulk import with placeholder currency symbols.
- **Deployment dashboard:** Staging checks (HTTP 200, plugin status) with redacted URLs.

## Anonymization Rules
- Blur/obscure any names, addresses, phone numbers, or booking IDs.
- Replace domains with `example.com` and emails with `user@example.com` before capture.
- Remove EXIF metadata using `exiftool -all=` and store compressed PNGs.
- Store files with neutral names (e.g., `catalog-admin-sanitized.png`).

## Storage Notes
- Screenshots live only in this folder; originals remain offline.
- Add a short caption per file describing context and checks performed.
