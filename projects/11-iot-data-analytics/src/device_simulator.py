"""Simulate IoT devices publishing telemetry to MQTT."""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Dict

import paho.mqtt.client as mqtt


@dataclass
class Device:
    identifier: str
    firmware_version: str

    def payload(self) -> Dict[str, float | str]:
        return {
            "device_id": self.identifier,
            "firmware": self.firmware_version,
            "temperature": round(random.uniform(18.0, 32.0), 2),
            "humidity": round(random.uniform(30.0, 70.0), 2),
            "battery": round(random.uniform(20.0, 100.0), 2),
            "timestamp": int(time.time()),
        }


def run_simulation(device_count: int, interval: float, broker: str, topic: str) -> None:
    client = mqtt.Client()
    client.connect(broker)
    devices = [Device(f"device-{i:03d}", "1.0.0") for i in range(device_count)]

    while True:
        for device in devices:
            message = json.dumps(device.payload())
            client.publish(topic, message)
            print(f"Published: {message}")
        time.sleep(interval)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IoT device simulator")
    parser.add_argument("--device-count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--broker", type=str, default="localhost")
    parser.add_argument("--topic", type=str, default="portfolio/telemetry")
    args = parser.parse_args()

    run_simulation(args.device_count, args.interval, args.broker, args.topic)
