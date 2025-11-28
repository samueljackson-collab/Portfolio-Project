# Project 5: Real-time Data Streaming

Kafka + Flink pipeline for processing portfolio events with exactly-once semantics.

## Run (local simulation)
```bash
pip install -r requirements.txt
python src/process_events.py
```

## Testing
```bash
# From repository root
python -m pytest projects/5-real-time-data-streaming/tests
```
