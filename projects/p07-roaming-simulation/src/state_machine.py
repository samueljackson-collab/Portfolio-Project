#!/usr/bin/env python3
"""
Roaming state machine implementation.

Manages subscriber state transitions during roaming scenarios.
"""
from enum import Enum
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubscriberState(Enum):
    """Subscriber roaming states."""

    IDLE = "idle"
    LOCATION_UPDATE = "location_update"
    AUTHENTICATING = "authenticating"
    ATTACHED = "attached"
    ROAMING = "roaming"
    DETACHED = "detached"
    REJECTED = "rejected"


class RoamingStateMachine:
    """State machine for roaming lifecycle."""

    def __init__(self, imsi: str):
        self.imsi = imsi
        self.state = SubscriberState.IDLE
        self.current_network = None
        self.home_network = None
        self.auth_attempts = 0
        self.max_auth_attempts = 3

    def initiate_roaming(self, home_network: str, visited_network: str) -> bool:
        """Initiate roaming to a visited network."""
        if self.state != SubscriberState.IDLE:
            logger.error(f"Cannot initiate roaming from state: {self.state}")
            return False

        self.home_network = home_network
        self.current_network = visited_network
        self.state = SubscriberState.LOCATION_UPDATE
        logger.info(f"IMSI {self.imsi}: Location update to {visited_network}")
        return True

    def authenticate(self, success: bool) -> bool:
        """Process authentication result."""
        if self.state != SubscriberState.LOCATION_UPDATE:
            logger.error(f"Cannot authenticate from state: {self.state}")
            return False

        self.state = SubscriberState.AUTHENTICATING
        self.auth_attempts += 1

        if success:
            self.state = SubscriberState.ATTACHED
            logger.info(f"IMSI {self.imsi}: Authentication successful, state=ATTACHED")
            return True
        else:
            if self.auth_attempts >= self.max_auth_attempts:
                self.state = SubscriberState.REJECTED
                logger.error(
                    f"IMSI {self.imsi}: Authentication rejected after {self.auth_attempts} attempts"
                )
            else:
                self.state = SubscriberState.LOCATION_UPDATE
                logger.warning(
                    f"IMSI {self.imsi}: Authentication failed, retry {self.auth_attempts}/{self.max_auth_attempts}"
                )
            return False

    def activate_roaming(self) -> bool:
        """Activate roaming services."""
        if self.state != SubscriberState.ATTACHED:
            logger.error(f"Cannot activate roaming from state: {self.state}")
            return False

        self.state = SubscriberState.ROAMING
        logger.info(f"IMSI {self.imsi}: Roaming activated on {self.current_network}")
        return True

    def detach(self) -> bool:
        """Detach from network (power off or out of coverage)."""
        if self.state in [SubscriberState.REJECTED, SubscriberState.DETACHED]:
            logger.warning(f"Already detached or rejected: {self.state}")
            return False

        self.state = SubscriberState.DETACHED
        logger.info(f"IMSI {self.imsi}: Detached from network")
        return True

    def get_state(self) -> SubscriberState:
        """Get current state."""
        return self.state

    def is_roaming(self) -> bool:
        """Check if subscriber is currently roaming."""
        return self.state == SubscriberState.ROAMING

    def reset(self):
        """Reset to idle state."""
        self.state = SubscriberState.IDLE
        self.current_network = None
        self.auth_attempts = 0
        logger.info(f"IMSI {self.imsi}: State machine reset to IDLE")
