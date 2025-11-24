"""Service layer for tracking multi-region deployments."""

from typing import Sequence
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ServiceDeployment
from app.schemas import DeploymentCreate, DeploymentDashboardResponse, DeploymentResponse, RegionRollup


async def create_deployment(
    db: AsyncSession,
    payload: DeploymentCreate,
    created_by: UUID | None,
) -> ServiceDeployment:
    """Persist a new deployment record."""

    deployment = ServiceDeployment(**payload.model_dump(), created_by=created_by)
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment


async def list_deployments(db: AsyncSession, limit: int = 20) -> Sequence[ServiceDeployment]:
    """Return recent deployment records ordered by update time."""

    result = await db.execute(
        select(ServiceDeployment)
        .order_by(ServiceDeployment.updated_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def deployment_dashboard(db: AsyncSession) -> DeploymentDashboardResponse:
    """Return aggregated deployment health by region with latest releases."""

    rollup_result = await db.execute(
        select(
            ServiceDeployment.region,
            func.count(ServiceDeployment.id),
            func.sum(ServiceDeployment.desired_replicas),
            func.sum(ServiceDeployment.available_replicas),
            func.count().filter(ServiceDeployment.status == "Healthy"),
        ).group_by(ServiceDeployment.region)
    )

    regions = [
        RegionRollup(
            region=row[0],
            services=row[1],
            desired_replicas=row[2] or 0,
            available_replicas=row[3] or 0,
            healthy=row[4] or 0,
        )
        for row in rollup_result.all()
    ]

    latest = await list_deployments(db, limit=10)
    latest_responses = [DeploymentResponse.model_validate(dep) for dep in latest]

    return DeploymentDashboardResponse(regions=regions, latest_releases=latest_responses)
