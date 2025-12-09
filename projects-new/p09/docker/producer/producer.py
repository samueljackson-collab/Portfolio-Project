import os
import time
import uuid
import requests

target = os.getenv("TARGET_URL", "http://consumer:8090/events")

while True:
    payload = {"id": str(uuid.uuid4()), "payload": "demo"}
    try:
        resp = requests.post(target, json=payload, timeout=3)
        print("sent", resp.status_code, flush=True)
    except Exception as exc:  # noqa: BLE001
        print("send failed", exc, flush=True)
    time.sleep(2)
