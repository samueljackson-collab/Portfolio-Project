"""Ransomware incident response simulator endpoints."""

from datetime import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import CurrentUser, DatabaseSession, raise_not_found
from app.models import Incident, IncidentEvent
from app.schemas import (
    IncidentCreate,
    IncidentEventCreate,
    IncidentEventResponse,
    IncidentResponse,
)
from app.services.security_simulations import simulated_incident_events, validate_incident_order


router = APIRouter(prefix="/incidents", tags=["Ransomware Response"])


async def _get_incident(db: AsyncSession, incident_id: str) -> Incident:
    inc_id = uuid.UUID(str(incident_id))
    incident = await db.get(Incident, inc_id)
    if not incident:
        raise_not_found("Incident")
    return incident


def _serialize_incident(incident: Incident, warning: Optional[str] = None) -> IncidentResponse:
    return IncidentResponse.model_validate(
        {
            "id": incident.id,
            "name": incident.name,
            "status": incident.status,
            "severity": incident.severity,
            "created_at": incident.created_at,
            "resolved_at": incident.resolved_at,
            "events": incident.events,
            "warning": warning,
        }
    )


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(payload: IncidentCreate, db: DatabaseSession, _: CurrentUser) -> IncidentResponse:
    incident = Incident(name=payload.name, severity=payload.severity)
    db.add(incident)
    await db.flush()
    await db.refresh(incident, attribute_names=["events"])
    return _serialize_incident(incident)


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(db: DatabaseSession) -> list[IncidentResponse]:
    result = await db.execute(select(Incident))
    incidents = result.scalars().unique().all()
    responses: list[IncidentResponse] = []
    for incident in incidents:
        await db.refresh(incident, attribute_names=["events"])
        responses.append(_serialize_incident(incident))
    return responses


@router.post("/{incident_id}/events", response_model=IncidentResponse)
async def add_incident_event(
    incident_id: str,
    payload: IncidentEventCreate,
    db: DatabaseSession,
    _: CurrentUser,
) -> IncidentResponse:
    incident = await _get_incident(db, incident_id)
    await db.refresh(incident, attribute_names=["events"])
    warning = validate_incident_order(incident.events, payload.type)

    sequence = len(incident.events)
    event = IncidentEvent(
        incident_id=incident.id,
        type=payload.type,
        details=payload.details,
        sequence=sequence,
        timestamp=payload.timestamp or (incident.created_at + (datetime.utcnow() - incident.created_at)),
    )
    db.add(event)
    await db.flush()
    await db.refresh(incident, attribute_names=["events"])
    return _serialize_incident(incident, warning)


@router.post("/{incident_id}/simulate", response_model=IncidentResponse)
async def simulate_incident(incident_id: str, db: DatabaseSession, _: CurrentUser) -> IncidentResponse:
    incident = await _get_incident(db, incident_id)
    await db.refresh(incident, attribute_names=["events"])
    start_index = len(incident.events)
    events = simulated_incident_events(incident, start_index=start_index)
    for event in events:
        event.incident_id = incident.id
        db.add(event)
    await db.flush()
    await db.refresh(incident, attribute_names=["events"])
    return _serialize_incident(incident)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(incident_id: str, db: DatabaseSession, _: CurrentUser) -> IncidentResponse:
    incident = await _get_incident(db, incident_id)
    incident.status = "resolved"
    incident.resolved_at = incident.resolved_at or datetime.utcnow()
    await db.flush()
    await db.refresh(incident, attribute_names=["events"])
    return _serialize_incident(incident)


@router.get("/{incident_id}/timeline", response_model=list[IncidentEventResponse])
async def get_timeline(incident_id: str, db: DatabaseSession) -> list[IncidentEvent]:
    incident_uuid = uuid.UUID(str(incident_id))
    await _get_incident(db, incident_uuid)
    result = await db.execute(
        select(IncidentEvent).where(IncidentEvent.incident_id == incident_uuid).order_by(IncidentEvent.sequence)
    )
    return result.scalars().all()
