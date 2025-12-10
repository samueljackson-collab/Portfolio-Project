# Playbook: Schema Drift Detected

1. **Trigger**: Alert `api_schema_drift > 0` from METRICS.
2. **Validate**: Re-run validator against `/openapi.json` and live responses.
3. **Mitigate**: Pin client version to last known good schema; notify API owner.
4. **Document**: File a change request using `REPORT_TEMPLATES/test_summary.md`.
5. **Close**: Add contract test covering the new/changed field.
