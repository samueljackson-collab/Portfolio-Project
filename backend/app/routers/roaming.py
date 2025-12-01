"""Roaming simulation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import (
    RoamingSessionCreate,
    RoamingSessionResponse,
    RoamingSessionListResponse,
    RoamingActionResponse,
)
from app.services.roaming import RoamingService, RoamingSession, RoamingState

router = APIRouter(prefix="/roaming", tags=["Roaming"])


def get_roaming_service() -> RoamingService:
    """Provide a shared roaming service instance."""
    # In-memory singleton for demo purposes
    if not hasattr(get_roaming_service, "_svc"):
        get_roaming_service._svc = RoamingService()
    return get_roaming_service._svc  # type: ignore[attr-defined]


@router.post(
    "/sessions",
    response_model=RoamingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_roaming_session(
    payload: RoamingSessionCreate,
    service: RoamingService = Depends(get_roaming_service),
) -> RoamingSession:
    """Start a roaming attempt for a subscriber."""
    session = service.create_session(
        imsi=payload.imsi,
        home_network=payload.home_network,
        visited_network=payload.visited_network,
    )
    return session


@router.post(
    "/sessions/{session_id}/authenticate",
    response_model=RoamingActionResponse,
)
async def authenticate_roaming_session(
    session_id: str,
    service: RoamingService = Depends(get_roaming_service),
) -> RoamingActionResponse:
    """Authenticate a session based on roaming agreements."""
    try:
        session = service.authenticate_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return RoamingActionResponse(
        session_id=session.session_id,
        state=session.state,
        message="Roaming authentication successful",
    )


@router.post(
    "/sessions/{session_id}/activate",
    response_model=RoamingActionResponse,
)
async def activate_roaming_session(
    session_id: str,
    service: RoamingService = Depends(get_roaming_service),
) -> RoamingActionResponse:
    """Activate data/voice services for an authenticated session."""
    try:
        session = service.activate_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return RoamingActionResponse(
        session_id=session.session_id,
        state=session.state,
        message="Roaming services activated",
    )


@router.post(
    "/sessions/{session_id}/detach",
    response_model=RoamingActionResponse,
)
async def detach_roaming_session(
    session_id: str,
    service: RoamingService = Depends(get_roaming_service),
) -> RoamingActionResponse:
    """Gracefully detach a subscriber from roaming."""
    try:
        session = service.detach_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return RoamingActionResponse(
        session_id=session.session_id,
        state=session.state,
        message="Session detached",
    )


@router.get("/sessions", response_model=RoamingSessionListResponse)
async def list_roaming_sessions(
    service: RoamingService = Depends(get_roaming_service),
) -> RoamingSessionListResponse:
    """List active roaming sessions and their states."""
    sessions = service.list_sessions()
    return RoamingSessionListResponse(
        total=len(sessions),
        sessions=sessions,
    )
