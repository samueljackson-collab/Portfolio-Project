"""Hybrid key exchange demonstration."""
from __future__ import annotations

import secrets
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


@dataclass
class KyberKeyPair:
    public_key: bytes
    secret_key: bytes


def kyber_generate_keypair() -> KyberKeyPair:
    # Placeholder for illustrative purposes
    public = secrets.token_bytes(32)
    secret = secrets.token_bytes(32)
    return KyberKeyPair(public, secret)


def kyber_encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
    shared_secret = hashes.Hash(hashes.SHA256())
    shared_secret.update(public_key)
    return secrets.token_bytes(32), shared_secret.finalize()


def kyber_decapsulate(secret_key: bytes, ciphertext: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(secret_key)
    digest.update(ciphertext)
    return digest.finalize()


def hybrid_key_exchange() -> bytes:
    kyber_keys = kyber_generate_keypair()
    ciphertext, kyber_secret_sender = kyber_encapsulate(kyber_keys.public_key)
    kyber_secret_receiver = kyber_decapsulate(kyber_keys.secret_key, ciphertext)

    private_key = ec.generate_private_key(ec.SECP384R1())
    peer_key = ec.generate_private_key(ec.SECP384R1())
    shared = private_key.exchange(ec.ECDH(), peer_key.public_key())

    combined = kyber_secret_sender + kyber_secret_receiver + shared
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"portfolio-hybrid")
    return hkdf.derive(combined)


if __name__ == "__main__":
    key = hybrid_key_exchange()
    print("Derived key (hex):", key.hex())
