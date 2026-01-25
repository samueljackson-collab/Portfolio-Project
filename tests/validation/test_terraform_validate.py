"""Terraform validation smoke tests for core infrastructure code."""

from __future__ import annotations

import os
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
        env={**os.environ, "TF_IN_AUTOMATION": "true"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform is not installed")
def test_terraform_init_and_validate() -> None:
    """Ensure terraform init/validate succeed against the root configuration."""

    init_result = _run([
        "terraform",
        f"-chdir={TERRAFORM_DIR}",
        "init",
        "-backend=false",
        "-input=false",
    ])
    if init_result.returncode != 0:
        pytest.fail(init_result.stdout + init_result.stderr)

    validate_result = _run([
        "terraform",
        f"-chdir={TERRAFORM_DIR}",
        "validate",
    ])
    if validate_result.returncode != 0:
        pytest.fail(validate_result.stdout + validate_result.stderr)
