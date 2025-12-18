"""Mini EDR platform simulation endpoints."""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession, raise_not_found
from app.models import EndpointAlert, EndpointAsset, EndpointPolicy
from app.schemas import (
    DeploymentSummary,
    EndpointAlertCreate,
    EndpointAlertResponse,
    EndpointCheckin,
    EndpointCreate,
    EndpointPolicyResponse,
    EndpointPolicyUpdate,
    EndpointResponse,
)
from app.services.security_simulations import deployment_summary, maybe_outdated_alert


router = APIRouter(prefix="/edr", tags=["EDR Simulation"])


DEFAULT_POLICIES = [
    EndpointPolicy(name="Ransomware Guard", description="Block unsigned encryptors", enabled=True),
    EndpointPolicy(name="PowerShell Constrained Mode", description="Force ConstrainedLanguageMode", enabled=True),
]


async def ensure_policies(db: DatabaseSession) -> None:
    result = await db.execute(select(EndpointPolicy))
    if result.scalars().first():
        return
    for policy in DEFAULT_POLICIES:
        db.add(policy)
    await db.flush()


@router.post("/endpoints", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def register_endpoint(payload: EndpointCreate, db: DatabaseSession, _: CurrentUser) -> EndpointAsset:
    endpoint = EndpointAsset(**payload.model_dump())
    db.add(endpoint)
    await db.flush()
    await db.refresh(endpoint)

    # Flag outdated agents on enrollment
    alert = maybe_outdated_alert(endpoint)
    if alert:
        alert.endpoint_id = endpoint.id
        db.add(alert)
        await db.flush()
    return endpoint


@router.get("/endpoints", response_model=list[EndpointResponse])
async def list_endpoints(db: DatabaseSession) -> list[EndpointAsset]:
    result = await db.execute(select(EndpointAsset))
    return result.scalars().all()


@router.post("/endpoints/{endpoint_id}/checkin", response_model=EndpointResponse)
async def endpoint_checkin(endpoint_id: str, payload: EndpointCheckin, db: DatabaseSession, _: CurrentUser) -> EndpointAsset:
    endpoint = await db.get(EndpointAsset, uuid.UUID(str(endpoint_id)))
    if not endpoint:
        raise_not_found("Endpoint")
    endpoint.last_checkin = datetime.utcnow()
    endpoint.online = True
    if payload.agent_version:
        endpoint.agent_version = payload.agent_version
    alert = maybe_outdated_alert(endpoint)
    if alert:
        alert.endpoint_id = endpoint.id
        db.add(alert)
        await db.flush()
    await db.flush()
    await db.refresh(endpoint)
    return endpoint


@router.get("/alerts", response_model=list[EndpointAlertResponse])
async def list_alerts(db: DatabaseSession) -> list[EndpointAlert]:
    result = await db.execute(select(EndpointAlert))
    return result.scalars().all()


@router.post("/alerts", response_model=EndpointAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(payload: EndpointAlertCreate, db: DatabaseSession, _: CurrentUser) -> EndpointAlert:
    alert = EndpointAlert(**payload.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@router.get("/policies", response_model=list[EndpointPolicyResponse])
async def list_policies(db: DatabaseSession) -> list[EndpointPolicy]:
    await ensure_policies(db)
    result = await db.execute(select(EndpointPolicy))
    return result.scalars().all()


@router.patch("/policies/{policy_id}", response_model=EndpointPolicyResponse)
async def toggle_policy(policy_id: str, payload: EndpointPolicyUpdate, db: DatabaseSession, _: CurrentUser) -> EndpointPolicy:
    policy = await db.get(EndpointPolicy, uuid.UUID(str(policy_id)))
    if not policy:
        raise_not_found("Policy")
    policy.enabled = payload.enabled
    await db.flush()
    await db.refresh(policy)
    return policy


@router.get("/deployment/summary", response_model=DeploymentSummary)
async def deployment_health(db: DatabaseSession) -> dict:
    result = await db.execute(select(EndpointAsset))
    endpoints = result.scalars().all()
    policies = (await db.execute(select(EndpointPolicy))).scalars().all()
    return deployment_summary(endpoints, policies)
