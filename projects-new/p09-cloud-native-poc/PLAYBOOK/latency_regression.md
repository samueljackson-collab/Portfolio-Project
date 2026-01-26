# Playbook: Latency Regression

1. **Trigger**: Alert `poc_latency_p95_ms > 250` for 5m.
2. **Verify**: Check pod resource limits; confirm no throttling.
3. **Scale**: Increase replicas via `kubectl scale deploy/poc-api --replicas=3`.
4. **Profile**: Enable uvicorn access logs and sample traces; inspect slow endpoints.
5. **Record**: Update `REPORT_TEMPLATES/release_report.md` with findings.
