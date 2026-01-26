"""Networking datacenter scaffold."""

from __future__ import annotations

from typing import Dict, List


def sample_topology() -> Dict[str, List[str]]:
    """Return a minimal topology map for use in placeholder diagrams/tests."""
    return {
        "core_switches": ["csw-1", "csw-2"],
        "edge_firewalls": ["fw-1"],
        "vlans": ["10-public", "20-app", "30-db"],
    }
