#!/usr/bin/env python3
"""
Mock HLR/HSS (Home Location Register / Home Subscriber Server).

Simulates subscriber authentication and roaming authorization.
"""
import hashlib
import logging
import random
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockHLR:
    """Mock HLR/HSS for roaming simulation."""

    def __init__(self):
        self.subscribers: Dict[str, Dict] = {}
        self.roaming_agreements: Dict[str, list] = {}

    def add_subscriber(self, imsi: str, msisdn: str, home_network: str, ki: str):
        """Add subscriber to HLR database."""
        self.subscribers[imsi] = {
            "msisdn": msisdn,
            "home_network": home_network,
            "ki": ki,  # Authentication key (K)
            "active": True,
            "roaming_enabled": True,
        }
        logger.info(f"Subscriber added: IMSI={imsi}, MSISDN={msisdn}")

    def add_roaming_agreement(self, home_network: str, visited_networks: list):
        """Configure roaming agreements."""
        self.roaming_agreements[home_network] = visited_networks
        logger.info(f"Roaming agreement: {home_network} <-> {visited_networks}")

    def validate_imsi(self, imsi: str) -> bool:
        """Validate IMSI format and existence."""
        if not imsi or len(imsi) != 15:
            logger.error(f"Invalid IMSI format: {imsi}")
            return False

        if imsi not in self.subscribers:
            logger.error(f"IMSI not found in HLR: {imsi}")
            return False

        return True

    def check_roaming_agreement(self, imsi: str, visited_network: str) -> bool:
        """Check if roaming is allowed between networks."""
        if not self.validate_imsi(imsi):
            return False

        subscriber = self.subscribers[imsi]
        home_network = subscriber["home_network"]

        if home_network == visited_network:
            logger.info(f"Subscriber on home network: {home_network}")
            return True

        allowed_networks = self.roaming_agreements.get(home_network, [])
        if visited_network in allowed_networks:
            logger.info(
                f"Roaming agreement exists: {home_network} -> {visited_network}"
            )
            return True
        else:
            logger.error(f"No roaming agreement: {home_network} -> {visited_network}")
            return False

    def generate_auth_vectors(self, imsi: str) -> Optional[Tuple[str, str, str]]:
        """Generate authentication vectors (RAND, SRES, Kc)."""
        if not self.validate_imsi(imsi):
            return None

        subscriber = self.subscribers[imsi]
        ki = subscriber["ki"]

        # Generate random challenge (RAND)
        rand = "".join([f"{random.randint(0, 255):02x}" for _ in range(16)])

        # Compute SRES (Signed Response) - simplified simulation
        sres = hashlib.md5((ki + rand).encode()).hexdigest()[:8]

        # Compute Kc (Ciphering Key) - simplified simulation
        kc = hashlib.md5((ki + rand + sres).encode()).hexdigest()[:16]

        logger.info(f"Auth vectors generated for IMSI {imsi}")
        return (rand, sres, kc)

    def authenticate(self, imsi: str, visited_network: str) -> bool:
        """Authenticate subscriber for roaming."""
        if not self.validate_imsi(imsi):
            return False

        subscriber = self.subscribers[imsi]

        if not subscriber["active"]:
            logger.error(f"Subscriber inactive: {imsi}")
            return False

        if not subscriber["roaming_enabled"]:
            logger.error(f"Roaming disabled for subscriber: {imsi}")
            return False

        if not self.check_roaming_agreement(imsi, visited_network):
            return False

        # Generate auth vectors (would be sent to VLR in real scenario)
        auth_vectors = self.generate_auth_vectors(imsi)
        if not auth_vectors:
            return False

        logger.info(f"Authentication successful: IMSI {imsi} on {visited_network}")
        return True

    def get_subscriber_info(self, imsi: str) -> Optional[Dict]:
        """Retrieve subscriber information."""
        return self.subscribers.get(imsi)
