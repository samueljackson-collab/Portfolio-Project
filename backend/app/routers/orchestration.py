"""Orchestration API endpoints for environment rollouts and tracking.

These routes are protected (require a valid JWT) and delegate all business
logic to OrchestrationService, which keeps plans and run history in memory.

WHY IN-MEMORY:
    For a portfolio demo, in-memory storage is sufficient. It avoids the need
    for a separate DB table while still demonstrating real API patterns.
    State is lost on server restart — this is intentional and documented.
"""

from typing import List
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
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
    _: User = Depends(get_current_user),
) -> List[OrchestrationPlan]:
    """Return the list of available orchestration plans.

    Plans are static (defined in OrchestrationService.__init__) and represent
    the three deployment environments: dev, staging, and production. They do
    not change at runtime.

    The `_` parameter enforces authentication without using the user object.
    Naming it `_` is a Python convention for "required but intentionally unused".
    """
    return service.list_plans()


@router.post(
    "/runs",
    response_model=OrchestrationRun,
    status_code=201,
)
async def start_run(
    request: OrchestrationRunRequest,
    service: OrchestrationService = Depends(get_orchestration_service),
    current_user: User = Depends(get_current_user),
) -> OrchestrationRun:
    """Start an orchestration run for the specified plan.

    The authenticated user's email is recorded as `requested_by` on the run
    record, providing an audit trail of who triggered each deployment.

    Args:
        request: Contains the plan_id and optional metadata (change ticket,
                 change window) passed through from the frontend console.
        current_user: Injected by FastAPI — the validated JWT user. Their email
                      is used to populate the run's audit field.

    Returns:
        The newly created run record, including its UUID, status, logs,
        artifact paths, and timestamps.

    Raises:
        404: If the plan_id does not match any known plan.
    """
    run = service.start_run(
        plan_id=request.plan_id,
        requested_by=current_user.email,
        parameters=request.parameters,
    )
    return OrchestrationRun.model_validate(run)


@router.get("/runs", response_model=List[OrchestrationRun])
async def list_runs(
    service: OrchestrationService = Depends(get_orchestration_service),
    _: User = Depends(get_current_user),
) -> List[OrchestrationRun]:
    """Return all recorded orchestration runs, sorted newest-first.

    `model_validate` converts the raw dict stored in the service into the
    typed Pydantic schema expected by the response model.
    """
    return [OrchestrationRun.model_validate(run) for run in service.list_runs()]


@router.get("/runs/{run_id}", response_model=OrchestrationRun)
async def get_run(
    run_id: str,
    service: OrchestrationService = Depends(get_orchestration_service),
    _: User = Depends(get_current_user),
) -> OrchestrationRun:
    """Return the details of a specific orchestration run by its UUID.

    Args:
        run_id: The UUID of the run to retrieve (from the URL path).

    Raises:
        404: If the run_id does not exist in the in-memory store.
    """
    run = service.get_run(run_id)
    return OrchestrationRun.model_validate(run)
