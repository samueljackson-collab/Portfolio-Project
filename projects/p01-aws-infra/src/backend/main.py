"""FastAPI backend scaffold for PRJ-AWS-001.

Provides health checks, configuration introspection, and a stubbed
infrastructure status endpoint to validate CI/CD deployments.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="PRJ-AWS-001 Backend", version="0.1.0")


class InfraStatus(BaseModel):
    stack_name: str
    region: str
    drift_detected: bool
    last_validation: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/status", response_model=InfraStatus)
def status() -> InfraStatus:
    return InfraStatus(
        stack_name="prj-aws-001-core",
        region="us-east-1",
        drift_detected=False,
        last_validation="not-yet-run",
    )
