"""Tests for advertising helpers."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.advertising.core import AdCreativeAI


def test_generate_handles_string_benefits_without_splitting() -> None:
    """Ensure a string is treated as a single benefit, not character by character."""

    ai = AdCreativeAI()
    benefits = "Instant hydration boost"

    result = ai.generate("Glow Serum", benefits=benefits)

    assert result["benefits"] == [benefits]
    assert benefits in result["headline"]
    assert benefits in result["copy"]
    assert "I, n, s" not in result["headline"]
