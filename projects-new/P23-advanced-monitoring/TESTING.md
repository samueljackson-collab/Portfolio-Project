# Testing

Automated commands:
- make lint
- k6 run tests/canary.js
- pytest tests/test_otel_pipeline.py

Manual validation:
- Verify OpenTelemetry collector receives and forwards test metrics to backend
- Validate canary alert thresholds fire correctly under simulated load
- Confirm dashboards ingest and display test data end-to-end
- Check that regional SLO burn-rate calculations match expected values
