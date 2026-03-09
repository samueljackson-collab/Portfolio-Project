# IoT Data Analytics Evidence Report (2026-01-21)

## Scope
- Generated sample telemetry for 10 devices over a 24-hour window.
- Ran ML-based anomaly detection and statistical checks using `src/ml_anomaly.py`.
- Produced dashboard-style overview and trend/anomaly charts.

## Data Ingestion Summary
- Records ingested: **2,880**
- Devices simulated: **10**
- Time range: **2026-01-20 00:00 → 2026-01-20 23:55**

## Analytics Summary
- Total anomalies detected (combined): **231**
- ML anomalies: **231**
- Temperature anomalies: **35**
- Battery anomalies: **19**

## Evidence Artifacts
- `sample_sensor_data.csv` — simulated telemetry input
- `anomaly_detection_results.csv` — enriched telemetry with anomaly flags
- `pipeline_summary.json` — ingestion + analytics summary metrics
- Dashboard and chart images were generated during the run but are not stored in the repo (binary artifacts removed).

## Notes
- Infrastructure deployment was attempted but blocked because Terraform is not installed in the environment. See `infrastructure_deploy.log` for details.
