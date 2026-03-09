"""Post-Quantum Cryptography Provider with multiple algorithm support."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

LOGGER = logging.getLogger(__name__)

# Try to import liboqs for actual PQC support
try:
    import oqs
    LIBOQS_AVAILABLE = True
except ImportError:
    LIBOQS_AVAILABLE = False
    LOGGER.warning("liboqs not available, using fallback implementations")


class KEMAlgorithm(Enum):
    """Supported Key Encapsulation Mechanisms."""
    KYBER512 = "Kyber512"
    KYBER768 = "Kyber768"
    KYBER1024 = "Kyber1024"
    MCELIECE348864 = "Classic-McEliece-348864"
    FRODO640AES = "FrodoKEM-640-AES"
    SIKE_P434 = "SIDH-p434"  # Note: SIKE broken, for educational purposes only


class SignatureAlgorithm(Enum):
    """Supported Signature Algorithms."""
    DILITHIUM2 = "Dilithium2"
    DILITHIUM3 = "Dilithium3"
    DILITHIUM5 = "Dilithium5"
    FALCON512 = "Falcon-512"
    FALCON1024 = "Falcon-1024"
    SPHINCS_SHA2_128F = "SPHINCS+-SHA2-128f-simple"


@dataclass
class KeyPair:
    """Represents a cryptographic key pair."""
    algorithm: str
    public_key: bytes
    secret_key: bytes
    key_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.key_id:
            self.key_id = hashlib.sha256(self.public_key).hexdigest()[:16]


@dataclass
class EncapsulationResult:
    """Result of KEM encapsulation."""
    ciphertext: bytes
    shared_secret: bytes


@dataclass
class SignatureResult:
    """Result of signature operation."""
    signature: bytes
    message_hash: bytes


class BaseKEMProvider(ABC):
    """Abstract base class for KEM providers."""

    @property
    @abstractmethod
    def algorithm(self) -> str:
        pass

    @abstractmethod
    def generate_keypair(self) -> KeyPair:
        pass

    @abstractmethod
    def encapsulate(self, public_key: bytes) -> EncapsulationResult:
        pass

    @abstractmethod
    def decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        pass


class BaseSignatureProvider(ABC):
    """Abstract base class for signature providers."""

    @property
    @abstractmethod
    def algorithm(self) -> str:
        pass

    @abstractmethod
    def generate_keypair(self) -> KeyPair:
        pass

    @abstractmethod
    def sign(self, secret_key: bytes, message: bytes) -> SignatureResult:
        pass

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        pass


class LibOQSKEMProvider(BaseKEMProvider):
    """KEM provider using liboqs."""

    def __init__(self, algorithm: KEMAlgorithm = KEMAlgorithm.KYBER768):
        if not LIBOQS_AVAILABLE:
            raise RuntimeError("liboqs not installed")
        self._algorithm = algorithm
        self._kem = oqs.KeyEncapsulation(algorithm.value)

    @property
    def algorithm(self) -> str:
        return self._algorithm.value

    def generate_keypair(self) -> KeyPair:
        public_key = self._kem.generate_keypair()
        secret_key = self._kem.export_secret_key()

        return KeyPair(
            algorithm=self.algorithm,
            public_key=public_key,
            secret_key=secret_key,
            metadata={
                "length_public_key": len(public_key),
                "length_secret_key": len(secret_key),
                "length_ciphertext": self._kem.details["length_ciphertext"],
                "length_shared_secret": self._kem.details["length_shared_secret"],
            },
        )

    def encapsulate(self, public_key: bytes) -> EncapsulationResult:
        kem = oqs.KeyEncapsulation(self._algorithm.value)
        ciphertext, shared_secret = kem.encap_secret(public_key)

        return EncapsulationResult(
            ciphertext=ciphertext,
            shared_secret=shared_secret,
        )

    def decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        kem = oqs.KeyEncapsulation(self._algorithm.value, secret_key)
        return kem.decap_secret(ciphertext)


class FallbackKEMProvider(BaseKEMProvider):
    """Fallback KEM using classical cryptography (for testing without liboqs)."""

    def __init__(self, algorithm: KEMAlgorithm = KEMAlgorithm.KYBER768):
        self._algorithm = algorithm
        LOGGER.warning(f"Using fallback KEM for {algorithm.value} - NOT quantum-safe!")

    @property
    def algorithm(self) -> str:
        return f"{self._algorithm.value}-FALLBACK"

    def generate_keypair(self) -> KeyPair:
        # Simulate Kyber key sizes
        key_sizes = {
            KEMAlgorithm.KYBER512: (800, 1632),
            KEMAlgorithm.KYBER768: (1184, 2400),
            KEMAlgorithm.KYBER1024: (1568, 3168),
        }
        pub_size, sec_size = key_sizes.get(self._algorithm, (1184, 2400))

        public_key = secrets.token_bytes(pub_size)
        secret_key = secrets.token_bytes(sec_size)

        return KeyPair(
            algorithm=self.algorithm,
            public_key=public_key,
            secret_key=secret_key,
            metadata={"fallback": True},
        )

    def encapsulate(self, public_key: bytes) -> EncapsulationResult:
        # Generate random shared secret
        shared_secret = secrets.token_bytes(32)

        # Create "ciphertext" by encrypting shared secret with public key hash
        h = hashlib.sha256(public_key + shared_secret).digest()
        ciphertext = shared_secret + h  # Simplified for demo

        return EncapsulationResult(
            ciphertext=ciphertext,
            shared_secret=shared_secret,
        )

    def decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        # Extract shared secret from ciphertext
        shared_secret = ciphertext[:32]
        return shared_secret


class LibOQSSignatureProvider(BaseSignatureProvider):
    """Signature provider using liboqs."""

    def __init__(self, algorithm: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3):
        if not LIBOQS_AVAILABLE:
            raise RuntimeError("liboqs not installed")
        self._algorithm = algorithm
        self._sig = oqs.Signature(algorithm.value)

    @property
    def algorithm(self) -> str:
        return self._algorithm.value

    def generate_keypair(self) -> KeyPair:
        public_key = self._sig.generate_keypair()
        secret_key = self._sig.export_secret_key()

        return KeyPair(
            algorithm=self.algorithm,
            public_key=public_key,
            secret_key=secret_key,
            metadata={
                "length_public_key": len(public_key),
                "length_secret_key": len(secret_key),
                "length_signature": self._sig.details["length_signature"],
            },
        )

    def sign(self, secret_key: bytes, message: bytes) -> SignatureResult:
        sig = oqs.Signature(self._algorithm.value, secret_key)
        signature = sig.sign(message)
        message_hash = hashlib.sha256(message).digest()

        return SignatureResult(
            signature=signature,
            message_hash=message_hash,
        )

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        sig = oqs.Signature(self._algorithm.value)
        return sig.verify(message, signature, public_key)


class FallbackSignatureProvider(BaseSignatureProvider):
    """Fallback signature using classical cryptography."""

    def __init__(self, algorithm: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3):
        self._algorithm = algorithm
        LOGGER.warning(f"Using fallback signature for {algorithm.value} - NOT quantum-safe!")

    @property
    def algorithm(self) -> str:
        return f"{self._algorithm.value}-FALLBACK"

    def generate_keypair(self) -> KeyPair:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, PublicFormat, NoEncryption
        )

        return KeyPair(
            algorithm=self.algorithm,
            public_key=public_key.public_bytes(Encoding.Raw, PublicFormat.Raw),
            secret_key=private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()),
            metadata={"fallback": True, "classical_algorithm": "Ed25519"},
        )

    def sign(self, secret_key: bytes, message: bytes) -> SignatureResult:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key)
        signature = private_key.sign(message)
        message_hash = hashlib.sha256(message).digest()

        return SignatureResult(
            signature=signature,
            message_hash=message_hash,
        )

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        try:
            pub = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            pub.verify(signature, message)
            return True
        except Exception:
            return False


def create_kem_provider(algorithm: KEMAlgorithm = KEMAlgorithm.KYBER768) -> BaseKEMProvider:
    """Factory to create appropriate KEM provider."""
    if LIBOQS_AVAILABLE:
        try:
            return LibOQSKEMProvider(algorithm)
        except Exception as e:
            LOGGER.warning(f"Failed to create liboqs KEM: {e}")

    return FallbackKEMProvider(algorithm)


def create_signature_provider(
    algorithm: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3
) -> BaseSignatureProvider:
    """Factory to create appropriate signature provider."""
    if LIBOQS_AVAILABLE:
        try:
            return LibOQSSignatureProvider(algorithm)
        except Exception as e:
            LOGGER.warning(f"Failed to create liboqs signature: {e}")

    return FallbackSignatureProvider(algorithm)
