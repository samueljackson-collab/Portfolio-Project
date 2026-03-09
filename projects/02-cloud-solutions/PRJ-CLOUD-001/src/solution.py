"""Cloud solutions placeholder module."""

from __future__ import annotations

from typing import Dict


def solution_profile() -> Dict[str, str]:
    """Return a static profile used by smoke tests and observability templates."""
    return {
        "name": "cloud-solutions",
        "owner": "architecture-guild",
        "status": "draft",
        "description": "Starter module describing the solution portfolio",
    }
