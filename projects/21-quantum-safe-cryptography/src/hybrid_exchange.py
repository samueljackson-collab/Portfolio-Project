"""Hybrid key exchange combining post-quantum and classical cryptography."""
from __future__ import annotations

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)

from .pqc_provider import (
    KEMAlgorithm,
    create_kem_provider,
    KeyPair,
    EncapsulationResult,
)

LOGGER = logging.getLogger(__name__)


@dataclass
class HybridKeyPair:
    """Combined PQC and classical key pair."""
    key_id: str
    pqc_keypair: KeyPair
    classical_private: bytes
    classical_public: bytes
    algorithm_pqc: str
    algorithm_classical: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_public_bundle(self) -> Dict[str, bytes]:
        """Get public keys for sharing."""
        return {
            "pqc_public": self.pqc_keypair.public_key,
            "classical_public": self.classical_public,
        }


@dataclass
class HybridEncapsulation:
    """Result of hybrid encapsulation."""
    pqc_ciphertext: bytes
    classical_public: bytes
    combined_hash: bytes


@dataclass
class SessionKey:
    """Derived session key from hybrid exchange."""
    key: bytes
    key_id: str
    algorithm: str
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class HybridKeyExchange:
    """
    Hybrid key exchange combining post-quantum KEM with classical ECDH.

    This provides defense-in-depth: even if one algorithm is broken,
    the other still provides security.
    """

    def __init__(
        self,
        pqc_algorithm: KEMAlgorithm = KEMAlgorithm.KYBER768,
        classical_curve: str = "x25519",
        key_length: int = 32,
    ):
        self.pqc_provider = create_kem_provider(pqc_algorithm)
        self.classical_curve = classical_curve
        self.key_length = key_length
        self._info = b"portfolio-hybrid-key-exchange-v1"

    def generate_keypair(self) -> HybridKeyPair:
        """Generate a hybrid key pair."""
        # Generate PQC keypair
        pqc_keypair = self.pqc_provider.generate_keypair()

        # Generate classical keypair
        if self.classical_curve == "x25519":
            classical_private_key = x25519.X25519PrivateKey.generate()
            classical_public = classical_private_key.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw
            )
            classical_private = classical_private_key.private_bytes(
                Encoding.Raw, PrivateFormat.Raw, NoEncryption()
            )
        else:
            # ECDH with P-384
            classical_private_key = ec.generate_private_key(ec.SECP384R1())
            classical_public = classical_private_key.public_key().public_bytes(
                Encoding.X962, PublicFormat.CompressedPoint
            )
            classical_private = classical_private_key.private_bytes(
                Encoding.DER, PrivateFormat.PKCS8, NoEncryption()
            )

        key_id = hashlib.sha256(
            pqc_keypair.public_key + classical_public
        ).hexdigest()[:16]

        return HybridKeyPair(
            key_id=key_id,
            pqc_keypair=pqc_keypair,
            classical_private=classical_private,
            classical_public=classical_public,
            algorithm_pqc=self.pqc_provider.algorithm,
            algorithm_classical=self.classical_curve,
        )

    def encapsulate(
        self,
        recipient_pqc_public: bytes,
        recipient_classical_public: bytes,
    ) -> Tuple[HybridEncapsulation, bytes]:
        """
        Encapsulate a shared secret for a recipient.

        Returns:
            Tuple of (encapsulation_data, shared_secret)
        """
        # PQC encapsulation
        pqc_result = self.pqc_provider.encapsulate(recipient_pqc_public)

        # Classical ECDH
        if self.classical_curve == "x25519":
            ephemeral_private = x25519.X25519PrivateKey.generate()
            ephemeral_public = ephemeral_private.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw
            )
            recipient_public = x25519.X25519PublicKey.from_public_bytes(
                recipient_classical_public
            )
            classical_shared = ephemeral_private.exchange(recipient_public)
        else:
            ephemeral_private = ec.generate_private_key(ec.SECP384R1())
            ephemeral_public = ephemeral_private.public_key().public_bytes(
                Encoding.X962, PublicFormat.CompressedPoint
            )
            recipient_public = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP384R1(), recipient_classical_public
            )
            classical_shared = ephemeral_private.exchange(ec.ECDH(), recipient_public)

        # Combine secrets using HKDF
        combined_input = pqc_result.shared_secret + classical_shared
        combined_hash = hashlib.sha256(combined_input).digest()

        shared_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=combined_hash,
            info=self._info,
        ).derive(combined_input)

        encapsulation = HybridEncapsulation(
            pqc_ciphertext=pqc_result.ciphertext,
            classical_public=ephemeral_public,
            combined_hash=combined_hash,
        )

        return encapsulation, shared_secret

    def decapsulate(
        self,
        keypair: HybridKeyPair,
        encapsulation: HybridEncapsulation,
    ) -> bytes:
        """
        Decapsulate to recover the shared secret.

        Args:
            keypair: Recipient's hybrid keypair
            encapsulation: Encapsulation data from sender

        Returns:
            The shared secret
        """
        # PQC decapsulation
        pqc_shared = self.pqc_provider.decapsulate(
            keypair.pqc_keypair.secret_key,
            encapsulation.pqc_ciphertext,
        )

        # Classical ECDH
        if self.classical_curve == "x25519":
            private_key = x25519.X25519PrivateKey.from_private_bytes(
                keypair.classical_private
            )
            sender_public = x25519.X25519PublicKey.from_public_bytes(
                encapsulation.classical_public
            )
            classical_shared = private_key.exchange(sender_public)
        else:
            from cryptography.hazmat.primitives.serialization import load_der_private_key
            private_key = load_der_private_key(keypair.classical_private, password=None)
            sender_public = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP384R1(), encapsulation.classical_public
            )
            classical_shared = private_key.exchange(ec.ECDH(), sender_public)

        # Combine secrets using HKDF
        combined_input = pqc_shared + classical_shared

        shared_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=encapsulation.combined_hash,
            info=self._info,
        ).derive(combined_input)

        return shared_secret

    def establish_session(
        self,
        local_keypair: HybridKeyPair,
        remote_public_bundle: Dict[str, bytes],
        session_ttl_seconds: int = 3600,
    ) -> SessionKey:
        """
        Establish a session key with a remote party.

        Args:
            local_keypair: Local hybrid keypair
            remote_public_bundle: Remote party's public keys
            session_ttl_seconds: Session key lifetime

        Returns:
            SessionKey for the session
        """
        encapsulation, shared_secret = self.encapsulate(
            remote_public_bundle["pqc_public"],
            remote_public_bundle["classical_public"],
        )

        key_id = hashlib.sha256(
            shared_secret + local_keypair.key_id.encode()
        ).hexdigest()[:16]

        return SessionKey(
            key=shared_secret,
            key_id=key_id,
            algorithm=f"hybrid-{self.pqc_provider.algorithm}-{self.classical_curve}",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=session_ttl_seconds),
            metadata={
                "pqc_ciphertext": encapsulation.pqc_ciphertext.hex(),
                "classical_public": encapsulation.classical_public.hex(),
            },
        )


def perform_key_exchange() -> bytes:
    """Perform a complete hybrid key exchange between two parties."""
    exchange = HybridKeyExchange()

    # Alice generates keypair
    alice_keypair = exchange.generate_keypair()
    LOGGER.info(f"Alice generated keypair: {alice_keypair.key_id}")

    # Bob generates keypair
    bob_keypair = exchange.generate_keypair()
    LOGGER.info(f"Bob generated keypair: {bob_keypair.key_id}")

    # Alice encapsulates for Bob
    encapsulation, alice_shared = exchange.encapsulate(
        bob_keypair.pqc_keypair.public_key,
        bob_keypair.classical_public,
    )

    # Bob decapsulates
    bob_shared = exchange.decapsulate(bob_keypair, encapsulation)

    # Verify both derived the same secret
    assert alice_shared == bob_shared, "Key exchange failed!"

    LOGGER.info(f"Key exchange successful, derived {len(alice_shared)} byte key")
    return alice_shared


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    key = perform_key_exchange()
    print(f"Derived key: {key.hex()}")
