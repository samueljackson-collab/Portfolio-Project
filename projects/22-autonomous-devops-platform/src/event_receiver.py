#!/usr/bin/env python3
"""
Event Receiver Module

Handles incoming events from various sources:
- Prometheus/Alertmanager webhooks
- Kubernetes events
- AWS CloudWatch events
- Custom application events
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from collections import deque
import hashlib

logger = logging.getLogger('event-receiver')


class EventSeverity(Enum):
    """Event severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventSource(Enum):
    """Event source types."""
    PROMETHEUS = "prometheus"
    ALERTMANAGER = "alertmanager"
    KUBERNETES = "kubernetes"
    CLOUDWATCH = "cloudwatch"
    CUSTOM = "custom"


@dataclass
class Event:
    """Represents an incoming event."""
    id: str
    event_type: str
    source: EventSource
    severity: EventSeverity
    title: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    fingerprint: str = ""
    status: str = "firing"

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> str:
        """Generate a unique fingerprint for deduplication."""
        content = f"{self.event_type}:{self.source.value}:{sorted(self.labels.items())}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "source": self.source.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "fingerprint": self.fingerprint,
            "status": self.status
        }


class EventDeduplicator:
    """Deduplicates events based on fingerprint and time window."""

    def __init__(self, window_seconds: int = 300):
        self.window_seconds = window_seconds
        self.seen_events: Dict[str, datetime] = {}

    def is_duplicate(self, event: Event) -> bool:
        """Check if an event is a duplicate within the time window."""
        now = datetime.utcnow()

        # Clean old entries
        self.seen_events = {
            fp: ts for fp, ts in self.seen_events.items()
            if (now - ts).total_seconds() < self.window_seconds
        }

        if event.fingerprint in self.seen_events:
            return True

        self.seen_events[event.fingerprint] = now
        return False


class EventReceiver:
    """
    Receives and processes events from multiple sources.

    Supports:
    - Webhook ingestion (HTTP)
    - Event deduplication
    - Priority-based processing
    - Integration with runbook engine
    """

    def __init__(self, runbook_engine=None, max_queue_size: int = 10000):
        self.runbook_engine = runbook_engine
        self.event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.event_history: deque = deque(maxlen=1000)
        self.deduplicator = EventDeduplicator()
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._event_counter = 0
        self.stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_deduplicated": 0,
            "by_source": {},
            "by_severity": {}
        }

    async def start(self):
        """Start the event processor."""
        self.running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("Event receiver started")

    async def stop(self):
        """Stop the event processor."""
        self.running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Event receiver stopped")

    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    async def receive_event(self, event: Event) -> bool:
        """
        Receive and queue an event for processing.

        Returns:
            True if event was queued, False if deduplicated
        """
        self.stats["total_received"] += 1
        self.stats["by_source"][event.source.value] = \
            self.stats["by_source"].get(event.source.value, 0) + 1
        self.stats["by_severity"][event.severity.value] = \
            self.stats["by_severity"].get(event.severity.value, 0) + 1

        # Check for duplicates
        if self.deduplicator.is_duplicate(event):
            self.stats["total_deduplicated"] += 1
            logger.debug(f"Deduplicated event: {event.fingerprint}")
            return False

        # Calculate priority (lower = higher priority)
        priority = self._calculate_priority(event)

        # Queue the event
        self._event_counter += 1
        await self.event_queue.put((priority, self._event_counter, event))
        self.event_history.append(event)

        logger.info(f"Queued event: {event.event_type} [{event.severity.value}]")
        return True

    def _calculate_priority(self, event: Event) -> int:
        """Calculate event priority (lower = higher priority)."""
        severity_priority = {
            EventSeverity.CRITICAL: 0,
            EventSeverity.HIGH: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.LOW: 3,
            EventSeverity.INFO: 4
        }
        return severity_priority.get(event.severity, 5)

    async def _process_events(self):
        """Process events from the queue."""
        while self.running:
            try:
                # Wait for an event with timeout
                try:
                    priority, counter, event = await asyncio.wait_for(
                        self.event_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                logger.info(f"Processing event: {event.event_type} [{event.id}]")

                # Execute handlers
                await self._execute_handlers(event)

                # Execute runbook if available
                if self.runbook_engine:
                    await self._execute_runbook(event)

                self.stats["total_processed"] += 1
                self.event_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _execute_handlers(self, event: Event):
        """Execute registered handlers for an event."""
        handlers = self.handlers.get(event.event_type, [])
        handlers.extend(self.handlers.get("*", []))  # Wildcard handlers

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    async def _execute_runbook(self, event: Event):
        """Execute appropriate runbook for an event."""
        try:
            await self.runbook_engine.execute_for_event(event)
        except Exception as e:
            logger.error(f"Runbook execution error: {e}")

    def parse_alertmanager_webhook(self, payload: Dict[str, Any]) -> List[Event]:
        """Parse Alertmanager webhook payload into events."""
        events = []

        for alert in payload.get("alerts", []):
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})

            severity_map = {
                "critical": EventSeverity.CRITICAL,
                "warning": EventSeverity.HIGH,
                "info": EventSeverity.INFO
            }
            severity = severity_map.get(
                labels.get("severity", "info"),
                EventSeverity.MEDIUM
            )

            event = Event(
                id=f"am-{alert.get('fingerprint', '')}",
                event_type=labels.get("alertname", "unknown"),
                source=EventSource.ALERTMANAGER,
                severity=severity,
                title=annotations.get("summary", labels.get("alertname", "Alert")),
                description=annotations.get("description", ""),
                metadata={
                    "startsAt": alert.get("startsAt"),
                    "endsAt": alert.get("endsAt"),
                    "generatorURL": alert.get("generatorURL")
                },
                labels=labels,
                status=alert.get("status", "firing")
            )
            events.append(event)

        return events

    def parse_kubernetes_event(self, payload: Dict[str, Any]) -> Event:
        """Parse Kubernetes event into internal event format."""
        metadata = payload.get("metadata", {})
        involved_object = payload.get("involvedObject", {})

        severity_map = {
            "Normal": EventSeverity.INFO,
            "Warning": EventSeverity.MEDIUM
        }

        return Event(
            id=f"k8s-{metadata.get('uid', '')}",
            event_type=payload.get("reason", "KubernetesEvent"),
            source=EventSource.KUBERNETES,
            severity=severity_map.get(payload.get("type"), EventSeverity.LOW),
            title=f"{involved_object.get('kind', 'Unknown')}/{involved_object.get('name', 'unknown')}: {payload.get('reason', '')}",
            description=payload.get("message", ""),
            metadata={
                "namespace": metadata.get("namespace"),
                "kind": involved_object.get("kind"),
                "name": involved_object.get("name"),
                "count": payload.get("count", 1)
            },
            labels={
                "namespace": metadata.get("namespace", ""),
                "kind": involved_object.get("kind", ""),
                "name": involved_object.get("name", "")
            }
        )

    def parse_cloudwatch_event(self, payload: Dict[str, Any]) -> Event:
        """Parse CloudWatch/EventBridge event into internal event format."""
        detail = payload.get("detail", {})

        return Event(
            id=f"cw-{payload.get('id', '')}",
            event_type=payload.get("detail-type", "CloudWatchEvent"),
            source=EventSource.CLOUDWATCH,
            severity=EventSeverity.MEDIUM,
            title=payload.get("detail-type", "CloudWatch Event"),
            description=json.dumps(detail),
            metadata={
                "account": payload.get("account"),
                "region": payload.get("region"),
                "resources": payload.get("resources", [])
            },
            labels={
                "source": payload.get("source", ""),
                "region": payload.get("region", "")
            }
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "history_size": len(self.event_history)
        }

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from history."""
        events = list(self.event_history)[-limit:]
        return [e.to_dict() for e in events]
