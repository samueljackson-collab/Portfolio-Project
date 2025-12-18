"""Simulation helpers for security-focused portfolio projects.

The helpers keep routers lean while documenting the reasoning used to
approximate realistic behavior (e.g., detection probabilities and event
sequencing). In production these routines would connect to dedicated
simulation engines or analytics backends, but here we keep them deterministic
enough for tests while remaining expressive for demonstration purposes.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, List, Optional

from app.models import (
    AnalysisReport,
    EndpointAlert,
    EndpointAsset,
    EndpointPolicy,
    Incident,
    IncidentEvent,
    MalwareSample,
    Operation,
    OperationEvent,
)


# ---------------------------------------------------------------------------
# Red team helpers
# ---------------------------------------------------------------------------

STEALTH_TACTICS = [
    "Credential harvesting via keylogging",
    "Slow lateral movement using WMI",
    "Living-off-the-land persistence scheduled task",
    "Domain enumeration with cached credentials",
    "Beacon jitter to avoid EDR baselines",
]


def detection_roll(stealth_factor: float, detection_confidence: float, seed: Optional[int] = None) -> bool:
    """Return True when an action is detected.

    The probability is inverted from the stealth factor (higher stealth means
    lower detection) and slightly biased by the event's detection confidence.
    An optional seed keeps behavior predictable in tests.
    """

    rng = random.Random(seed)
    base_detection_probability = max(0.05, 1 - stealth_factor)
    noisy_bonus = (1 - detection_confidence) * 0.2
    probability = min(0.95, base_detection_probability + noisy_bonus)
    return rng.random() < probability


def build_operation_event(operation: Operation, day: int, seed: Optional[int] = None) -> OperationEvent:
    """Create a simulated event for the requested day.

    The timestamp is derived from the operation start date, and the category is
    selected deterministically when a seed is supplied to keep tests stable.
    """

    rng = random.Random(seed)
    category = rng.choice(["Initial Access", "Lateral Movement", "Persistence", "Command and Control"])
    description = rng.choice(STEALTH_TACTICS)
    detection_confidence = rng.uniform(0.35, 0.85)
    detected = detection_roll(operation.stealth_factor, detection_confidence, seed=seed)
    timestamp = (operation.start_date or datetime.utcnow()) + timedelta(days=day)

    return OperationEvent(
        day=day,
        timestamp=timestamp,
        description=description,
        category=category,
        detected=detected,
        detection_confidence=detection_confidence,
    )


def update_operation_status(operation: Operation, event: OperationEvent) -> None:
    """Update streak and detection metadata when a new event arrives."""

    operation.days_elapsed = max(operation.days_elapsed or 0, event.day)
    if event.detected:
        operation.undetected_streak = 0
        operation.first_detection_at = operation.first_detection_at or event.timestamp
        operation.status = "detected"
    else:
        operation.undetected_streak = (operation.undetected_streak or 0) + 1


# ---------------------------------------------------------------------------
# Ransomware helpers
# ---------------------------------------------------------------------------

INCIDENT_SEQUENCE = [
    ("Detection", "SOC console raises a ransomware pattern match"),
    ("Containment", "Isolate affected hosts and disable credentials"),
    ("Eradication", "Remove malicious binaries and scheduled tasks"),
    ("Recovery", "Restore from clean backups and validate integrity"),
    ("LessonsLearned", "Document gaps and tune detections"),
]


def simulated_incident_events(incident: Incident, start_index: int = 0) -> List[IncidentEvent]:
    """Build a deterministic sequence of lifecycle events.

    Each event is spaced thirty minutes apart to make ordering obvious in
    timelines and reports.
    """

    events: List[IncidentEvent] = []
    base_time = incident.created_at or datetime.utcnow()
    for offset, (event_type, detail) in enumerate(INCIDENT_SEQUENCE[start_index:], start=start_index):
        events.append(
            IncidentEvent(
                type=event_type,
                details=detail,
                sequence=offset,
                timestamp=base_time + timedelta(minutes=30 * offset),
            )
        )
    return events


def validate_incident_order(existing_events: Iterable[IncidentEvent], new_type: str) -> Optional[str]:
    """Return a warning string when events arrive out of order."""

    expected_next = len(list(existing_events))
    stage_names = [stage for stage, _ in INCIDENT_SEQUENCE]
    if new_type not in stage_names:
        return "Unknown event type supplied"
    if stage_names.index(new_type) != expected_next:
        return f"Expected {stage_names[expected_next]} but received {new_type}"
    return None


# ---------------------------------------------------------------------------
# Malware analysis helpers
# ---------------------------------------------------------------------------


def simulated_analysis(sample: MalwareSample) -> AnalysisReport:
    """Produce a deterministic analysis report for a sample.

    The heuristics intentionally mirror common sandbox summaries: hash prefixes
    imply packer use, file names imply families, and we synthesize a YARA rule
    that analysts can copy into their tooling.
    """

    hash_hint = sample.file_hash[:6]
    static_lines = [
        f"Identified hash prefix {hash_hint} suggesting lightweight packer",
        f"Sample type: {sample.sample_type}",
    ]
    family = sample.family or ("ransom" if "lock" in sample.name.lower() else "unknown")
    dynamic_lines = [
        "Simulated dynamic run captured mutex creation and beacon callback",
        f"Behavior consistent with {family} tooling",
    ]
    iocs = [f"domain-{hash_hint}.example.com", f"C2/{family}/{hash_hint}"]
    rule_name = sample.name.replace(" ", "_").lower()
    yara_rule = (
        f"rule {rule_name} \n{{\n  meta:\n    author = \"portfolio-lab\"\n"
        f"    family = \"{family}\"\n  strings:\n    $hash = \"{hash_hint}\"\n"
        "  condition:\n    all of them\n}"
    )

    return AnalysisReport(
        static_analysis="; ".join(static_lines),
        dynamic_analysis="; ".join(dynamic_lines),
        iocs=iocs,
        yara_rule=yara_rule,
    )


# ---------------------------------------------------------------------------
# EDR helpers
# ---------------------------------------------------------------------------


def maybe_outdated_alert(endpoint: EndpointAsset, minimum_version: str = "1.5.0") -> Optional[EndpointAlert]:
    """Create an alert when the agent version lags behind the baseline."""

    def version_tuple(value: str) -> tuple[int, int, int]:
        parts = value.split(".")
        return tuple(int(part) for part in (parts + ["0", "0", "0"])[:3])

    if version_tuple(endpoint.agent_version) < version_tuple(minimum_version):
        return EndpointAlert(
            endpoint_id=endpoint.id,
            severity="high",
            description=f"Agent {endpoint.agent_version} below baseline {minimum_version}",
        )
    return None


def deployment_summary(endpoints: List[EndpointAsset], policies: List[EndpointPolicy]) -> dict:
    """Compute aggregate deployment coverage statistics."""

    total = len(endpoints)
    online = len([e for e in endpoints if e.online])
    outdated = len([e for e in endpoints if maybe_outdated_alert(e)])
    coverage = 0 if total == 0 else round((online / total) * 100, 2)
    active_policies = len([p for p in policies if p])
    return {
        "total_endpoints": total,
        "online": online,
        "outdated_agents": outdated,
        "coverage": coverage,
        "active_policies": active_policies,
    }
