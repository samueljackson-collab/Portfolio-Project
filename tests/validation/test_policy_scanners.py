"""Policy-as-code checks using tfsec and Checkov."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = REPO_ROOT / "terraform"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(shutil.which("tfsec") is None, reason="tfsec is not installed")
def test_tfsec_scan() -> None:
    """Execute tfsec against the root Terraform configuration."""

    result = _run(["tfsec", str(TERRAFORM_DIR), "--no-color", "--minimum-severity", "LOW"])
    if result.returncode != 0:
        pytest.fail(result.stdout + result.stderr)


@pytest.mark.skipif(shutil.which("checkov") is None, reason="checkov is not installed")
def test_checkov_scan() -> None:
    """Execute Checkov against the root Terraform configuration."""

    result = _run(["checkov", "-d", str(TERRAFORM_DIR), "--quiet", "--framework", "terraform"])
    if result.returncode != 0:
        pytest.fail(result.stdout + result.stderr)
