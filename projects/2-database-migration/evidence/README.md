# Migration Evidence

This folder captures deployment and validation artifacts for the demo stack defined in `compose.demo.yml`.

## Status
- Docker is not available in this execution environment, so the demo stack could not be started.
- The files below capture the attempted commands and intended validation steps.

## Artifacts
- `stack-deploy.log` — Docker Compose deployment attempt and error output.
- `migration-run.log` — Orchestrator launch attempt and error output.
- `schema-before-source.txt` — Intended source schema capture (pre-migration).
- `schema-before-target.txt` — Intended target schema capture (pre-migration).
- `schema-after-source.txt` — Intended source schema capture (post-migration).
- `schema-after-target.txt` — Intended target schema capture (post-migration).
- `row-count-validation.txt` — Intended row-count validation commands.
- `timing-chart.md` — Throughput chart placeholder and data requirements.

## Next Steps (when Docker is available)
1. Start the demo stack: `docker compose -f compose.demo.yml up -d`.
2. Capture schema snapshots from source/target (before and after migration).
3. Run the migration orchestrator and capture logs.
4. Validate row counts or checksums and compute rows/sec throughput.
