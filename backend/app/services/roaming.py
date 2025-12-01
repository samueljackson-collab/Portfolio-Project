"""Roaming service domain logic for simulation endpoints."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid


class RoamingState(str, Enum):
    """Lifecycle state for a roaming session."""

    IDLE = "idle"
    ATTACHED = "attached"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    DETACHED = "detached"


@dataclass
class RoamingSession:
    """In-memory representation of a roaming attempt."""

    session_id: str
    imsi: str
    home_network: str
    visited_network: str
    state: RoamingState = RoamingState.IDLE
    authenticated: bool = False
    activated: bool = False
    events: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def record(self, message: str) -> None:
        timestamped = f"{datetime.utcnow().isoformat()}Z - {message}"
        self.events.append(timestamped)
        self.last_updated = datetime.utcnow()


class RoamingService:
    """Coordinate roaming session lifecycle and validations."""

    def __init__(self, roaming_agreements: Optional[Dict[str, List[str]]] = None):
        self.roaming_agreements = roaming_agreements or {
            "310-410": ["208-01", "234-15", "262-01"],
            "208-01": ["310-410", "234-15", "262-01"],
        }
        self.sessions: Dict[str, RoamingSession] = {}

    def _get_session(self, session_id: str) -> RoamingSession:
        if session_id not in self.sessions:
            raise KeyError(f"Unknown session id {session_id}")
        return self.sessions[session_id]

    def create_session(self, imsi: str, home_network: str, visited_network: str) -> RoamingSession:
        session_id = str(uuid.uuid4())
        session = RoamingSession(
            session_id=session_id,
            imsi=imsi,
            home_network=home_network,
            visited_network=visited_network,
            state=RoamingState.ATTACHED,
        )
        session.record("Session created and subscriber attached to visited network")
        self.sessions[session_id] = session
        return session

    def authenticate_session(self, session_id: str) -> RoamingSession:
        session = self._get_session(session_id)
        allowed_networks = self.roaming_agreements.get(session.home_network, [])
        if session.visited_network not in allowed_networks:
            session.record("Roaming denied: no roaming agreement between networks")
            session.state = RoamingState.DETACHED
            raise PermissionError("No roaming agreement for visited network")

        session.authenticated = True
        session.state = RoamingState.AUTHENTICATED
        session.record("Subscriber authenticated for roaming")
        return session

    def activate_session(self, session_id: str) -> RoamingSession:
        session = self._get_session(session_id)
        if not session.authenticated:
            session.record("Activation blocked: session not authenticated")
            raise PermissionError("Cannot activate unauthenticated session")

        session.activated = True
        session.state = RoamingState.ACTIVE
        session.record("Roaming data and voice services activated")
        return session

    def detach_session(self, session_id: str) -> RoamingSession:
        session = self._get_session(session_id)
        session.state = RoamingState.DETACHED
        session.record("Subscriber detached from visited network")
        return session

    def list_sessions(self) -> List[RoamingSession]:
        return list(self.sessions.values())

    def reset(self) -> None:
        self.sessions.clear()
