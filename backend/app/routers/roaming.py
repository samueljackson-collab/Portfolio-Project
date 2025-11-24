"""Roaming simulation API endpoints.

Provides REST endpoints that wrap the roaming session store so operators can
validate attach/roam flows without the full simulator harness.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.schemas import (
    RoamingAgreementsResponse,
    RoamingEventRequest,
    RoamingSessionCreate,
    RoamingSessionResponse,
)
from app.services.roaming import get_roaming_store, RoamingSessionStore

router = APIRouter(prefix="/roaming", tags=["Roaming"])


def _serialize_session(session) -> RoamingSessionResponse:
    return RoamingSessionResponse(
        session_id=session.session_id,
        imsi=session.imsi,
        home_network=session.home_network,
        visited_network=session.visited_network,
        state=session.state.value,
        events=[
            {
                "type": event.type,
                "message": event.message,
                "timestamp": event.timestamp,
            }
            for event in session.events
        ],
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/agreements", response_model=RoamingAgreementsResponse, status_code=status.HTTP_200_OK)
async def list_roaming_agreements(store: RoamingSessionStore = Depends(get_roaming_store)):
    """List roaming agreements that control whether sessions can be initiated."""
    return RoamingAgreementsResponse(agreements=store.list_agreements())


@router.post("/sessions", response_model=RoamingSessionResponse, status_code=status.HTTP_201_CREATED)
async def initiate_roaming(payload: RoamingSessionCreate, store: RoamingSessionStore = Depends(get_roaming_store)):
    """Create a roaming session if agreements allow it."""
    session = store.create_session(
        imsi=payload.imsi,
        home_network=payload.home_network,
        visited_network=payload.visited_network,
        roaming_enabled=payload.roaming_enabled,
    )
    return _serialize_session(session)


@router.post(
    "/sessions/{session_id}/events",
    response_model=RoamingSessionResponse,
    status_code=status.HTTP_200_OK,
)
async def add_roaming_event(
    session_id: UUID,
    payload: RoamingEventRequest,
    store: RoamingSessionStore = Depends(get_roaming_store),
):
    """Append a new roaming event and update the simulated state machine."""
    session = store.add_event(session_id=session_id, event_type=payload.type, message=payload.message)
    return _serialize_session(session)


@router.get("/sessions/{session_id}", response_model=RoamingSessionResponse, status_code=status.HTTP_200_OK)
async def get_roaming_session(session_id: UUID, store: RoamingSessionStore = Depends(get_roaming_store)):
    """Fetch current session state and event history."""
    session = store.get_session(session_id)
    return _serialize_session(session)

