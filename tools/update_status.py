#!/usr/bin/env python3
"""Update STATUS_BOARD.md completion percentages."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "STATUS_BOARD.md"

PATTERN = re.compile(r"(\d+)%")


def main() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    matches = PATTERN.findall(text)
    if not matches:
        print("No percentages found in STATUS_BOARD.md")
        return
    avg = sum(int(m) for m in matches) / len(matches)
    summary_line = f"Average completion: {avg:.1f}% across {len(matches)} tracked areas."
    print(summary_line)


if __name__ == "__main__":
    main()
