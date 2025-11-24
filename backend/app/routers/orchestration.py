"""Deployment orchestration API surface.

Tracks orchestration runs, emits status updates, and exposes a summary for
the React console. The in-memory store keeps responses deterministic for
testing while remaining lightweight for the demo stack.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Lifecycle states for orchestration runs."""

    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class StepEvent(BaseModel):
    """Individual step event for a run."""

    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = "info"


class OrchestrationRun(BaseModel):
    """Full representation of an orchestration run."""

    id: str
    name: str
    environment: str
    target_version: str
    status: RunStatus
    started_at: datetime
    updated_at: datetime
    steps: List[StepEvent] = Field(default_factory=list)


class RunRequest(BaseModel):
    """Request payload for starting an orchestration run."""

    name: str
    environment: str
    target_version: str
    kickoff_notes: Optional[str] = None


class RunUpdate(BaseModel):
    """Request payload for appending events or transitioning status."""

    message: str
    status: Optional[RunStatus] = None
    level: str = "info"


class OrchestrationStore:
    """Minimal in-memory store for orchestration runs."""

    def __init__(self) -> None:
        self._runs: Dict[str, OrchestrationRun] = {}

    def create_run(self, payload: RunRequest) -> OrchestrationRun:
        run_id = str(uuid4())
        now = datetime.utcnow()
        kickoff_message = payload.kickoff_notes or "Deployment orchestrator started"
        run = OrchestrationRun(
            id=run_id,
            name=payload.name,
            environment=payload.environment,
            target_version=payload.target_version,
            status=RunStatus.running,
            started_at=now,
            updated_at=now,
            steps=[StepEvent(message=kickoff_message, level="info", timestamp=now)],
        )
        self._runs[run_id] = run
        return run

    def list_runs(self) -> List[OrchestrationRun]:
        return list(self._runs.values())

    def get_run(self, run_id: str) -> OrchestrationRun:
        run = self._runs.get(run_id)
        if not run:
            raise KeyError(run_id)
        return run

    def append_event(self, run_id: str, update: RunUpdate) -> OrchestrationRun:
        run = self.get_run(run_id)
        event = StepEvent(message=update.message, level=update.level)
        events = list(run.steps) + [event]
        status = update.status or run.status
        refreshed = run.copy(update={"steps": events, "status": status, "updated_at": datetime.utcnow()})
        self._runs[run_id] = refreshed
        return refreshed

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {state.value: 0 for state in RunStatus}
        for run in self._runs.values():
            counts[run.status.value] += 1
        return counts


store = OrchestrationStore()
router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


@router.post("/runs", response_model=OrchestrationRun, status_code=201)
def start_run(payload: RunRequest) -> OrchestrationRun:
    """Start a new orchestration run."""

    return store.create_run(payload)


@router.get("/runs", response_model=List[OrchestrationRun])
def list_runs() -> List[OrchestrationRun]:
    """List all orchestration runs."""

    return store.list_runs()


@router.get("/runs/{run_id}", response_model=OrchestrationRun)
def get_run(run_id: str) -> OrchestrationRun:
    """Retrieve a single orchestration run."""

    try:
        return store.get_run(run_id)
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=404, detail="Run not found") from exc


@router.post("/runs/{run_id}/events", response_model=OrchestrationRun)
def add_run_event(run_id: str, update: RunUpdate) -> OrchestrationRun:
    """Append an event to a run and optionally transition its status."""

    try:
        return store.append_event(run_id, update)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


@router.get("/summary")
def get_summary() -> Dict[str, int]:
    """Provide a lightweight status summary for dashboards."""

    return store.summary()
