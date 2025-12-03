# Report Templates — P08

## API Test Summary
- **Scope:** endpoints exercised, environment, build ID.
- **Results:** pass/fail counts, response-time percentiles, schema validation incidents.
- **Evidence:** Newman HTML + JUnit artifacts, curl repro snippets, environment variables (redacted).

## Defect Report
- Endpoint + verb
- Request payload + headers (scrubbed)
- Expected vs actual status/body
- Correlation ID / trace ID
- Steps to reproduce with Newman command and environment

## Latency Baseline
- Table of p50/p90/p99 per endpoint from `reports/perf.json`.
- Comparison to previous run; highlight regressions >10%.
