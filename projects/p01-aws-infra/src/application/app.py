"""Application orchestrator for PRJ-AWS-001 scaffolds.

This module wires together the backend API, frontend assets, and
CloudFormation utilities so local developers can quickly run
end-to-end smoke tests before pushing changes to CI/CD.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = ROOT / "src" / "backend" / "main.py"
FRONTEND_DIR = ROOT / "src" / "frontend"


def run_backend() -> None:
    """Start the FastAPI backend with uvicorn."""
    subprocess.run([
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ], cwd=BACKEND_APP.parent, check=True)


def run_frontend() -> None:
    """Run the frontend dev server (Vite-compatible)."""
    subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
    subprocess.run(["npm", "run", "dev", "--", "--host", "0.0.0.0"], cwd=FRONTEND_DIR, check=True)


def run_tests() -> None:
    """Execute unit tests for backend and shared utilities."""
    subprocess.run(["pytest", "-q", "tests"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="PRJ-AWS-001 local orchestrator")
    parser.add_argument(
        "command",
        choices=["backend", "frontend", "test"],
        help="Component to run",
    )
    args = parser.parse_args()

    if args.command == "backend":
        run_backend()
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "test":
        run_tests()


if __name__ == "__main__":
    main()
