#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load_plan(path: Path):
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    return data[0]["Plan"] if isinstance(data, list) else data["Plan"]


def summarize_node(node, depth=0, lines=None):
    if lines is None:
        lines = []
    indent = "  " * depth
    node_type = node.get("Node Type", "Unknown")
    total_cost = node.get("Total Cost", "?")
    plan_rows = node.get("Plan Rows", "?")
    actual_time = node.get("Actual Total Time", "?")
    lines.append(
        f"{indent}- {node_type} | cost={total_cost} rows={plan_rows} time={actual_time}"
    )

    for child in node.get("Plans", []):
        summarize_node(child, depth + 1, lines)
    return lines


def main():
    if len(sys.argv) < 2:
        print("Usage: explain_analyzer.py <explain.json>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    plan = load_plan(path)
    lines = summarize_node(plan)
    output = "\n".join(lines)
    print(output)


if __name__ == "__main__":
    main()
