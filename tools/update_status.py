#!/usr/bin/env python3
"""Update STATUS_BOARD.md with completion percentages based on task files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Tuple

STATUS_TEMPLATE = """# Status Board\n\n| Area | Status | Notes |\n|------|--------|-------|\n| Backend service | {backend_status} | {backend_notes} |\n| Frontend service | {frontend_status} | {frontend_notes} |\n| Infrastructure | {infra_status} | {infra_notes} |\n| Monitoring | {monitoring_status} | {monitoring_notes} |\n| Testing | {testing_status} | {testing_notes} |\n| Documentation | {docs_status} | {docs_notes} |\n| Automation tooling | {automation_status} | {automation_notes} |\n"""


STATUS_MAP = {
    "complete": "🟢 Complete",
    "in_progress": "🟠 In Progress",
    "planned": "🔵 Planned",
}


def load_completion(task_csv: Path) -> Tuple[int, int]:
    completed = 0
    total = 0
    with task_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += 1
            if row.get("status", "").lower() == "done":
                completed += 1
    return completed, total


def determine_status(completed: int, total: int) -> str:
    if total == 0:
        return STATUS_MAP["planned"]
    ratio = completed / total
    if ratio >= 0.9:
        return STATUS_MAP["complete"]
    if ratio >= 0.4:
        return STATUS_MAP["in_progress"]
    return STATUS_MAP["planned"]


def build_notes(completed: int, total: int) -> str:
    if total == 0:
        return "No tasks tracked"
    return f"{completed}/{total} tasks complete"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("tasks/ai_tasks_v1.4.csv"))
    parser.add_argument("--output", type=Path, default=Path("STATUS_BOARD.md"))
    args = parser.parse_args()

    completed, total = load_completion(args.csv)
    status = determine_status(completed, total)
    notes = build_notes(completed, total)

    content = STATUS_TEMPLATE.format(
        backend_status=status,
        backend_notes=notes,
        frontend_status=status,
        frontend_notes=notes,
        infra_status=status,
        infra_notes=notes,
        monitoring_status=status,
        monitoring_notes=notes,
        testing_status=status,
        testing_notes=notes,
        docs_status=status,
        docs_notes=notes,
        automation_status=status,
        automation_notes=notes,
    )
    args.output.write_text(content)
    print(f"Status board updated ({completed}/{total} complete)")


if __name__ == "__main__":
    main()
