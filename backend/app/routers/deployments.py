"""Endpoints for tracking multi-region deployments and release health."""

from typing import Optional

from fastapi import APIRouter, Depends, status

from app.dependencies import CurrentUser, DatabaseSession, get_optional_user
from app.models import User
from app.schemas import (
    DeploymentCreate,
    DeploymentDashboardResponse,
    DeploymentResponse,
)
from app.services.deployment_service import (
    create_deployment,
    deployment_dashboard,
    list_deployments,
)

router = APIRouter(prefix="/deployments", tags=["Operations"])


@router.get("", response_model=list[DeploymentResponse])
async def get_deployments(
    db: DatabaseSession,
    current_user: Optional[User] = Depends(get_optional_user),
) -> list[DeploymentResponse]:
    """Return the most recent deployment records for observability dashboards."""

    deployments = await list_deployments(db=db)
    return [DeploymentResponse.model_validate(dep) for dep in deployments]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DeploymentResponse,
)
async def post_deployment(
    payload: DeploymentCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DeploymentResponse:
    """Create a new deployment record (authenticated)."""

    deployment = await create_deployment(
        db=db,
        payload=payload,
        created_by=current_user.id,
    )
    return DeploymentResponse.model_validate(deployment)


@router.get("/dashboard", response_model=DeploymentDashboardResponse)
async def get_dashboard(db: DatabaseSession) -> DeploymentDashboardResponse:
    """Get aggregated deployment posture for the operator console."""

    return await deployment_dashboard(db=db)
