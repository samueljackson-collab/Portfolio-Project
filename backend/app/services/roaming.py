"""Roaming simulation service layer.

This module provides an in-memory roaming session store mirroring the
telecom simulator behaviors so the API can be exercised without an HLR/HSS
backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status


class RoamingState(str, Enum):
    """Supported roaming lifecycle states."""

    INITIATED = "initiated"
    AUTHENTICATING = "authenticating"
    ATTACHED = "attached"
    ROAMING = "roaming"
    DETACHED = "detached"
    FAILED = "failed"


@dataclass
class RoamingEvent:
    """Event recorded against a roaming session."""

    type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoamingSession:
    """In-memory roaming session representation."""

    session_id: UUID
    imsi: str
    home_network: str
    visited_network: str
    state: RoamingState = RoamingState.INITIATED
    events: List[RoamingEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_event(self, event_type: str, message: str, new_state: Optional[RoamingState] = None) -> None:
        self.events.append(RoamingEvent(type=event_type, message=message))
        if new_state:
            self.state = new_state
        self.updated_at = datetime.utcnow()


class RoamingSessionStore:
    """Stateful manager for roaming sessions and agreements."""

    def __init__(self) -> None:
        self.sessions: Dict[UUID, RoamingSession] = {}
        self.roaming_agreements: Dict[str, List[str]] = {
            "310-410": ["208-01", "234-15"],
            "208-01": ["310-410", "262-01"],
        }

    def create_session(self, *, imsi: str, home_network: str, visited_network: str, roaming_enabled: bool) -> RoamingSession:
        if not roaming_enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Roaming disabled for subscriber",
            )

        if not self.check_roaming_agreement(home_network, visited_network):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No roaming agreement between networks",
            )

        session_id = uuid4()
        session = RoamingSession(
            session_id=session_id,
            imsi=imsi,
            home_network=home_network,
            visited_network=visited_network,
            state=RoamingState.AUTHENTICATING,
        )
        session.add_event(
            "authenticate",
            f"Authentication started for IMSI {imsi} on {visited_network}",
            new_state=RoamingState.AUTHENTICATING,
        )
        self.sessions[session_id] = session
        return session

    def check_roaming_agreement(self, home_network: str, visited_network: str) -> bool:
        allowed = self.roaming_agreements.get(home_network, [])
        return visited_network in allowed or visited_network == home_network

    def add_event(self, session_id: UUID, event_type: str, message: str) -> RoamingSession:
        session = self.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        if event_type == "authenticate":
            session.add_event(event_type, message, new_state=RoamingState.AUTHENTICATING)
        elif event_type == "location_update":
            session.add_event(event_type, message, new_state=RoamingState.ATTACHED)
        elif event_type == "activate_roaming":
            session.add_event(event_type, message, new_state=RoamingState.ROAMING)
        elif event_type == "detach":
            session.add_event(event_type, message, new_state=RoamingState.DETACHED)
        else:
            session.add_event(event_type, message)
        return session

    def get_session(self, session_id: UUID) -> RoamingSession:
        session = self.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session

    def list_agreements(self) -> Dict[str, List[str]]:
        return self.roaming_agreements


def get_roaming_store() -> RoamingSessionStore:
    """Provide singleton-style store for dependency injection."""

    # Using function attribute to maintain singleton across imports
    if not hasattr(get_roaming_store, "_store"):
        get_roaming_store._store = RoamingSessionStore()
    return get_roaming_store._store  # type: ignore[attr-defined]

