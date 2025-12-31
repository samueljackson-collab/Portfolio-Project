# Runbook: Newman CI Pipeline Failure

1. **Check Logs**: Download JUnit/JSON from CI artifact.
2. **Reproduce Locally**:
   ```bash
   newman run producer/collections/core.postman_collection.json -e producer/env/local.postman_environment.json --reporters cli,junit
   ```
3. **Inspect Failures**: Identify status code or schema mismatches.
4. **Stabilize Data**: Refresh mock data in `producer/examples/` if snapshots changed legitimately.
5. **Rerun**: Trigger CI rerun; ensure metrics show zero drift.
