# Runbooks — P08

## Runbook: Execute Full Suite Locally
1. Install dependencies: `npm install`.
2. Start mock server: `docker-compose -f docker/compose.api.yaml up -d mock`
3. Run `make test` to hit mock endpoints.
4. Review `reports/newman/*.html` for failures.

## Runbook: Contract Drift Check
1. Set `BASE_URL` to staging.
2. Run `make test-contract ENV=staging`.
3. Inspect `reports/contract-diff.json` for mismatches.
4. If drift detected, open ADR + align schema or API implementation.

## Runbook: Publish Evidence to CI Artifact Store
1. After CI run, collect `reports/newman/*.xml` and `reports/perf.json`.
2. Upload to artifact bucket/folder labeled with build ID.
3. Update `REPORT_TEMPLATES` summary with links.
