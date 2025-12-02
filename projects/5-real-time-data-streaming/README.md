# Project 5: Real-time Data Streaming

Kafka + Flink pipeline for processing portfolio events with exactly-once semantics.

## Architecture
- **Context:** Producers emit operational events that must be validated, enriched, and delivered to multiple downstream stores with low latency.
- **Decision:** Use Kafka as the durable event backbone with Schema Registry for compatibility checks, Flink for stateful stream processing, and dual sinks (data lake + OLAP) for both batch and realtime consumers.
- **Consequences:** Achieves exactly-once guarantees and replayable history, but requires strong observability on lag, checkpoint health, and schema evolution to avoid pipeline regressions.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Run (local simulation)
```bash
pip install -r requirements.txt
python src/process_events.py
```
