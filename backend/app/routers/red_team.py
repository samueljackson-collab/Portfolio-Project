"""Routes for the red team operation simulator.

The simulator records a day-by-day adversary campaign. Mutation routes
require authentication while read-only timelines remain public to allow quick
demo consumption from the UI.
"""

from datetime import datetime, timedelta
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DatabaseSession, CurrentUser, raise_not_found
from app.models import Operation, OperationEvent
from app.schemas import (
    OperationCreate,
    OperationEventCreate,
    OperationEventResponse,
    OperationResponse,
)
from app.services.security_simulations import build_operation_event, update_operation_status


router = APIRouter(prefix="/red-team", tags=["Red Team Simulator"])


async def _get_operation(db: AsyncSession, operation_id: str) -> Operation:
    op_id = uuid.UUID(str(operation_id))
    operation = await db.get(Operation, op_id)
    if not operation:
        raise_not_found("Operation")
    return operation


@router.post("/operations", response_model=OperationResponse, status_code=status.HTTP_201_CREATED)
async def create_operation(
    payload: OperationCreate,
    db: DatabaseSession,
    _: CurrentUser,
) -> Operation:
    """Create a new simulated campaign.

    Auth is enforced to mirror real-world controls on red team scheduling.
    """

    operation = Operation(
        name=payload.name,
        objective=payload.objective,
        start_date=payload.start_date or datetime.utcnow(),
        stealth_factor=payload.stealth_factor,
    )
    db.add(operation)
    await db.flush()
    await db.refresh(operation)
    return operation


@router.get("/operations", response_model=list[OperationResponse])
async def list_operations(db: DatabaseSession) -> list[Operation]:
    """List all campaigns with their timelines for dashboard summaries."""

    result = await db.execute(select(Operation).options())
    operations = result.scalars().unique().all()
    for op in operations:
        # Load events eagerly for summary counts
        await db.refresh(op, attribute_names=["events"])
    return operations


@router.post("/operations/{operation_id}/events", response_model=OperationEventResponse)
async def add_operation_event(
    operation_id: str,
    payload: OperationEventCreate,
    db: DatabaseSession,
    _: CurrentUser,
) -> OperationEvent:
    """Record a specific action in the campaign timeline."""

    operation = await _get_operation(db, operation_id)

    # Determine day sequencing. Operations are capped to 90 days to stay within
    # the requested APT length while still allowing deterministic tests.
    result = await db.execute(
        select(func.max(OperationEvent.day)).where(OperationEvent.operation_id == operation.id)
    )
    max_day = result.scalar() or 0
    day = payload.day or max_day + 1
    if day > 90:
        raise HTTPException(status_code=400, detail="Operation timeline exceeds 90 days")

    timestamp = payload.timestamp or (operation.start_date + timedelta(days=day))
    event = OperationEvent(
        operation_id=operation.id,
        day=day,
        timestamp=timestamp,
        description=payload.description,
        category=payload.category,
        detected=payload.detected,
        detection_confidence=payload.detection_confidence,
    )
    update_operation_status(operation, event)
    db.add(event)
    await db.flush()
    await db.refresh(event)
    await db.refresh(operation)
    return event


@router.post("/operations/{operation_id}/simulate-next-day", response_model=OperationEventResponse)
async def simulate_next_day(
    operation_id: str,
    db: DatabaseSession,
    _: CurrentUser,
    seed: Optional[int] = Query(None, description="Optional seed for deterministic tests"),
) -> OperationEvent:
    """Automatically create a stealthy action for the next day.

    Detection probability is controlled by the operation stealth factor and the
    generated event confidence. The seed keeps CI reliable.
    """

    operation = await _get_operation(db, operation_id)
    result = await db.execute(
        select(func.max(OperationEvent.day)).where(OperationEvent.operation_id == operation.id)
    )
    day = (result.scalar() or 0) + 1
    if day > 90:
        raise HTTPException(status_code=400, detail="Operation timeline exceeds 90 days")

    event = build_operation_event(operation, day=day, seed=seed)
    event.operation_id = operation.id
    update_operation_status(operation, event)
    db.add(event)
    await db.flush()
    await db.refresh(event)
    await db.refresh(operation)
    return event


@router.post("/operations/{operation_id}/mark-detected", response_model=OperationResponse)
async def mark_detected(operation_id: str, db: DatabaseSession, _: CurrentUser) -> Operation:
    """Mark an operation as detected without creating a new event."""

    operation = await _get_operation(db, operation_id)
    operation.first_detection_at = operation.first_detection_at or datetime.utcnow()
    operation.status = "detected"
    operation.undetected_streak = 0
    await db.flush()
    await db.refresh(operation)
    return operation


@router.get("/operations/{operation_id}/timeline", response_model=list[OperationEventResponse])
async def get_timeline(
    operation_id: str,
    db: DatabaseSession,
    category: Optional[str] = Query(None),
    detected: Optional[bool] = Query(None),
) -> list[OperationEvent]:
    """Fetch a filtered view of the campaign timeline for dashboards."""

    operation_uuid = uuid.UUID(str(operation_id))
    await _get_operation(db, operation_uuid)
    stmt = select(OperationEvent).where(OperationEvent.operation_id == operation_uuid)
    if category:
        stmt = stmt.where(OperationEvent.category == category)
    if detected is not None:
        stmt = stmt.where(OperationEvent.detected == detected)
    stmt = stmt.order_by(OperationEvent.day)
    result = await db.execute(stmt)
    return result.scalars().all()
