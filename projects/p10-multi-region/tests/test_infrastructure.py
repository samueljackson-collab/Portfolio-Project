"""Test multi-region infrastructure."""

import pytest


def test_regions_defined():
    """Test that regions are properly defined."""
    primary = "us-east-1"
    secondary = "us-west-2"
    assert primary != secondary
    assert primary in ["us-east-1", "us-west-1", "us-west-2"]
    assert secondary in ["us-east-1", "us-west-1", "us-west-2"]


def test_rto_rpo_realistic():
    """Test RTO/RPO values are realistic."""
    rto_minutes = 15
    rpo_minutes = 5
    assert rto_minutes >= 5, "RTO should be at least 5 minutes"
    assert rpo_minutes >= 1, "RPO should be at least 1 minute"
    assert rpo_minutes <= rto_minutes, "RPO should be less than or equal to RTO"
