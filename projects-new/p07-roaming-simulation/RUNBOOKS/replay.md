# Runbook: Replay Stored Roaming Batches

1. **Prerequisites**: Ensure `out/events.jsonl` is available or download from object storage.
2. **Start Services**:
   ```bash
   docker compose -f docker/compose.roaming.yaml up consumer
   ```
3. **Replay**:
   ```bash
   python consumer/main.py --ingest-file out/events.jsonl --metrics-port 9200
   ```
4. **Verify KPIs**: Check `http://localhost:9200/metrics` for `roaming_attach_success` and `roaming_latency_p95`.
5. **Archive Results**: Save KPIs to `reports/` with timestamp and attach to incident ticket if applicable.
