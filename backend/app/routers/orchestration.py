"""Orchestration API endpoints for environment rollouts and tracking."""

from typing import List
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas import (
    OrchestrationPlan,
    OrchestrationRun,
    OrchestrationRunRequest,
)
from app.services.orchestration_service import (
    get_orchestration_service,
    OrchestrationService,
)

router = APIRouter(
    prefix="/orchestration",
    tags=["Orchestration"],
)


@router.get("/plans", response_model=List[OrchestrationPlan])
async def list_plans(
    service: OrchestrationService = Depends(get_orchestration_service),
    _: object = Depends(get_current_user),
) -> List[OrchestrationPlan]:
    """Return available orchestration plans."""
    return service.list_plans()


@router.post(
    "/runs",
    response_model=OrchestrationRun,
    status_code=201,
)
async def start_run(
    request: OrchestrationRunRequest,
    service: OrchestrationService = Depends(get_orchestration_service),
    current_user: object = Depends(get_current_user),
) -> OrchestrationRun:
    """Start a run for the given plan and annotate it with user metadata."""
    run = service.start_run(
        plan_id=request.plan_id,
        requested_by=getattr(current_user, "email", "system"),
        parameters=request.parameters,
    )
    return OrchestrationRun.model_validate(run)


@router.get("/runs", response_model=List[OrchestrationRun])
async def list_runs(
    service: OrchestrationService = Depends(get_orchestration_service),
    _: object = Depends(get_current_user),
) -> List[OrchestrationRun]:
    """Return recorded orchestration runs."""
    return [OrchestrationRun.model_validate(run) for run in service.list_runs()]


@router.get("/runs/{run_id}", response_model=OrchestrationRun)
async def get_run(
    run_id: str,
    service: OrchestrationService = Depends(get_orchestration_service),
    _: object = Depends(get_current_user),
) -> OrchestrationRun:
    """Get details for a specific orchestration run."""
    run = service.get_run(run_id)
    return OrchestrationRun.model_validate(run)
