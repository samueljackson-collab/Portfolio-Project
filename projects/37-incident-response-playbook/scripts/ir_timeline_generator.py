#!/usr/bin/env python3
"""
IR Timeline Generator

Reads a JSON incident log and produces a formatted chronological timeline
with MTTD, MTTC, and MTTR calculations.

Usage:
    python ir_timeline_generator.py [--incident-file FILE] [--output FILE]
    python ir_timeline_generator.py --demo
"""

import argparse
import json
import sys
from datetime import datetime, timezone


DEMO_INCIDENT = {
    "incident_id": "INC-2026-0042",
    "incident_type": "Ransomware — LockBit 3.0",
    "severity": "P1",
    "events": [
        {
            "time": "2026-01-15T07:52:00Z",
            "phase": "Initial Access",
            "actor": "Attacker",
            "description": "User jsmith opens malicious Word attachment (CVE-2024-21413)",
            "system": "JSMITH-WS"
        },
        {
            "time": "2026-01-15T07:54:00Z",
            "phase": "Execution",
            "actor": "Attacker",
            "description": "WINWORD.EXE spawns PowerShell; EDR medium-severity alert fired",
            "system": "JSMITH-WS"
        },
        {
            "time": "2026-01-15T08:01:00Z",
            "phase": "Lateral Movement",
            "actor": "Attacker",
            "description": "PsExec lateral movement to FIN-SRV-01 and FIN-SRV-02",
            "system": "FIN-SRV-01, FIN-SRV-02"
        },
        {
            "time": "2026-01-15T08:03:00Z",
            "phase": "Impact",
            "actor": "Attacker",
            "description": "Volume Shadow Copy deletion on FIN-SRV-01 (vssadmin.exe)",
            "system": "FIN-SRV-01"
        },
        {
            "time": "2026-01-15T08:07:00Z",
            "phase": "Impact",
            "actor": "Attacker",
            "description": "First .lockbit encrypted files detected — EDR escalates to HIGH",
            "system": "FIN-SRV-01"
        },
        {
            "time": "2026-01-15T08:14:00Z",
            "phase": "Detection",
            "actor": "SOC",
            "description": "SOC Analyst acknowledges alert; IC declared; bridge call opened",
            "system": "SOC"
        },
        {
            "time": "2026-01-15T08:29:00Z",
            "phase": "Containment",
            "actor": "SOC",
            "description": "All 3 affected hosts isolated via CrowdStrike console",
            "system": "FIN-SRV-01, FIN-SRV-02, JSMITH-WS"
        },
        {
            "time": "2026-01-15T08:41:00Z",
            "phase": "Containment",
            "actor": "SOC",
            "description": "C2 IPs added to perimeter block list",
            "system": "Firewall"
        },
        {
            "time": "2026-01-15T09:01:00Z",
            "phase": "Containment",
            "actor": "SOC",
            "description": "Containment confirmed — no further spread detected",
            "system": "Network"
        },
        {
            "time": "2026-01-15T09:15:00Z",
            "phase": "Eradication",
            "actor": "IR Team",
            "description": "Forensic image of FIN-SRV-01 captured",
            "system": "FIN-SRV-01"
        },
        {
            "time": "2026-01-15T11:30:00Z",
            "phase": "Eradication",
            "actor": "IR Team",
            "description": "Root cause confirmed: CVE-2024-21413 + weak MFA on jsmith",
            "system": "JSMITH-WS"
        },
        {
            "time": "2026-01-15T14:28:00Z",
            "phase": "Recovery",
            "actor": "Infra",
            "description": "FIN-SRV-01 restored from 2026-01-14 backup — validated",
            "system": "FIN-SRV-01"
        },
        {
            "time": "2026-01-15T14:44:00Z",
            "phase": "Recovery",
            "actor": "Infra",
            "description": "FIN-SRV-02 restored from backup",
            "system": "FIN-SRV-02"
        },
        {
            "time": "2026-01-15T15:06:00Z",
            "phase": "Recovery",
            "actor": "IT",
            "description": "jsmith workstation rebuilt from golden image — user access restored",
            "system": "JSMITH-WS"
        }
    ]
}

# Key event markers for metric calculation
DETECTION_MARKER = "Detection"
CONTAINMENT_MARKER = "Containment"
RECOVERY_MARKER = "Recovery"
INITIAL_COMPROMISE_MARKER = "Initial Access"


def parse_time(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def format_duration(seconds: float) -> str:
    mins = int(seconds // 60)
    if mins < 60:
        return f"{mins} min"
    hours = mins // 60
    remaining_mins = mins % 60
    return f"{hours}h {remaining_mins}m"


def generate_timeline(incident: dict) -> str:
    lines = []
    inc_id = incident.get("incident_id", "UNKNOWN")
    inc_type = incident.get("incident_type", "Unknown")
    severity = incident.get("severity", "Unknown")
    events = sorted(incident["events"], key=lambda e: e["time"])

    lines.append("=" * 72)
    lines.append(f"  INCIDENT TIMELINE — {inc_id}")
    lines.append(f"  Type: {inc_type} | Severity: {severity}")
    lines.append("=" * 72)
    lines.append("")

    # Collect key timestamps for metrics
    first_event = None
    detection_time = None
    first_containment = None
    recovery_complete = None

    for ev in events:
        t = parse_time(ev["time"])
        phase = ev.get("phase", "")
        actor = ev.get("actor", "")
        system = ev.get("system", "")
        description = ev.get("description", "")

        if first_event is None:
            first_event = t
        if detection_time is None and phase == DETECTION_MARKER:
            detection_time = t
        if first_containment is None and phase == CONTAINMENT_MARKER:
            first_containment = t
        if phase == RECOVERY_MARKER:
            recovery_complete = t

        time_str = t.strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"  {time_str}  [{phase:20s}]  [{actor:10s}]")
        lines.append(f"    → {description}")
        lines.append(f"      System: {system}")
        lines.append("")

    # Metrics
    lines.append("-" * 72)
    lines.append("  METRICS")
    lines.append("-" * 72)

    if first_event and detection_time:
        mttd = (detection_time - first_event).total_seconds()
        lines.append(f"  MTTD (Mean Time to Detect):   {format_duration(mttd)}")
    else:
        lines.append("  MTTD: insufficient data")

    if detection_time and first_containment:
        mttc = (first_containment - detection_time).total_seconds()
        lines.append(f"  MTTC (Mean Time to Contain):  {format_duration(mttc)}")
    else:
        lines.append("  MTTC: insufficient data")

    if first_containment and recovery_complete:
        mttr = (recovery_complete - first_containment).total_seconds()
        lines.append(f"  MTTR (Mean Time to Recover):  {format_duration(mttr)}")
    else:
        lines.append("  MTTR: insufficient data")

    if first_event and recovery_complete:
        total = (recovery_complete - first_event).total_seconds()
        lines.append(f"  Total incident duration:       {format_duration(total)}")

    lines.append("")
    lines.append(f"  Total events: {len(events)}")
    phases = {}
    for ev in events:
        phases[ev.get("phase", "Unknown")] = phases.get(ev.get("phase", "Unknown"), 0) + 1
    for phase, count in sorted(phases.items()):
        lines.append(f"    {phase}: {count}")
    lines.append("")
    lines.append("=" * 72)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="IR Timeline Generator")
    parser.add_argument("--incident-file", help="Path to incident JSON file")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--demo", action="store_true", help="Run with demo incident data")
    args = parser.parse_args()

    if args.demo:
        incident = DEMO_INCIDENT
    elif args.incident_file:
        with open(args.incident_file) as f:
            incident = json.load(f)
    else:
        print("Error: provide --incident-file or --demo", file=sys.stderr)
        sys.exit(1)

    output = generate_timeline(incident)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Timeline written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
