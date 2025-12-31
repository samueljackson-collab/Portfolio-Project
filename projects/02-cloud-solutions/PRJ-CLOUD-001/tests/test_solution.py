"""Smoke test for the cloud solutions scaffold."""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import solution  # type: ignore  # noqa: E402


def test_solution_profile_has_expected_fields():
    profile = solution.solution_profile()
    assert profile["name"] == "cloud-solutions"
    assert profile["status"] == "draft"
    assert set(profile.keys()) == {"name", "owner", "status", "description"}
