# Standard Operating Procedures — P08

## Daily Validation
- Run `make smoke` against mock server; ensure no regressions.
- Check for updated Postman env files and rotate secrets if older than 30 days.

## Change Control
- New endpoints require schema addition under `tests/schemas/` and coverage entry in `reports/coverage-matrix.md`.
- Mask sensitive headers in report outputs (`--reporter-htmlextra-hideRequestHeaders`).

## Data Hygiene
- Do not commit real tokens; only `.example` files stored in repo.
- Scrub request/response bodies before attaching to incidents using `scripts/sanitize_payloads.sh`.
