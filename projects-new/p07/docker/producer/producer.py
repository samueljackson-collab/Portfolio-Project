import json
import os
import time
import uuid
from kafka import KafkaProducer
import yaml

bootstrap = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
scenario_path = os.getenv("SCENARIO_PATH", "/app/jobs/scenarios/demo.yaml")
topic = "roaming.events"

producer = KafkaProducer(
    bootstrap_servers=bootstrap,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    linger_ms=20,
    enable_idempotence=True,
)

with open(scenario_path, "r", encoding="utf-8") as f:
    scenario = yaml.safe_load(f)

def build_event(template):
    return {
        "event_id": str(uuid.uuid4()),
        "imsi": template["imsi"],
        "cell_id": template["cell_id"],
        "country": template["country"],
        "event": template.get("event", "attach"),
        "timestamp": int(time.time() * 1000),
    }

while True:
    for template in scenario.get("events", []):
        event = build_event(template)
        producer.send(topic, key=event["imsi"].encode(), value=event)
    producer.flush()
    time.sleep(float(scenario.get("interval_seconds", 5)))
