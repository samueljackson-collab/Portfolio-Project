"""Unit tests for main module."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import health_check


def test_health_check():
    """Test health check returns expected structure."""
    result = health_check()

    assert "status" in result
    assert "version" in result
    assert result["status"] == "healthy"
