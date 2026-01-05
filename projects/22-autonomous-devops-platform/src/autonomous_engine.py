"""Autonomous remediation engine sample."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class Event:
    type: str
    severity: str
    metadata: Dict[str, str]


class RunbookRegistry:
    def __init__(self) -> None:
        self.registry: Dict[str, Callable[[Event], None]] = {}

    def register(self, key: str, handler: Callable[[Event], None]) -> None:
        self.registry[key] = handler

    def execute(self, event: Event) -> None:
        handler = self.registry.get(event.type)
        if handler:
            handler(event)
        else:
            print(f"No automation defined for {event.type}")


def scale_service(event: Event) -> None:
    print(f"Scaling service {event.metadata['service']} to handle load")


def restart_pod(event: Event) -> None:
    print(
        f"Restarting pod {event.metadata['pod']} in namespace {event.metadata['namespace']}"
    )


def main() -> None:
    registry = RunbookRegistry()
    registry.register("latency_alert", scale_service)
    registry.register("pod_crash", restart_pod)

    sample_events = [
        Event("latency_alert", "high", {"service": "api"}),
        Event("pod_crash", "medium", {"pod": "worker-123", "namespace": "default"}),
    ]

    for event in sample_events:
        registry.execute(event)


if __name__ == "__main__":
    main()
