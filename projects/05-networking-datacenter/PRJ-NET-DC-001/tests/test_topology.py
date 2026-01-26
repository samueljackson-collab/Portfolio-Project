"""Tests for the datacenter topology scaffold."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import topology  # type: ignore  # noqa: E402


def test_sample_topology_has_core_and_vlans():
    topo = topology.sample_topology()
    assert "core_switches" in topo and len(topo["core_switches"]) == 2
    assert "vlans" in topo and "10-public" in topo["vlans"]
