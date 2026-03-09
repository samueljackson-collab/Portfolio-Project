"""FastAPI REST API for Quantum-Safe Cryptography Service."""
from __future__ import annotations

import base64
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .pqc_provider import (
    KEMAlgorithm,
    SignatureAlgorithm,
    create_kem_provider,
    create_signature_provider,
    LIBOQS_AVAILABLE,
)
from .hybrid_exchange import HybridKeyExchange, HybridKeyPair, SessionKey

LOGGER = logging.getLogger(__name__)

# Prometheus metrics
KEYPAIRS_GENERATED = Counter(
    "pqc_keypairs_generated_total",
    "Total keypairs generated",
    ["algorithm"]
)
ENCAPSULATIONS = Counter(
    "pqc_encapsulations_total",
    "Total encapsulations performed",
    ["algorithm"]
)
SIGNATURES = Counter(
    "pqc_signatures_total",
    "Total signatures generated",
    ["algorithm"]
)
OPERATION_LATENCY = Histogram(
    "pqc_operation_latency_seconds",
    "Operation latency in seconds",
    ["operation"]
)

# In-memory key store (use proper HSM/KMS in production)
key_store: Dict[str, HybridKeyPair] = {}
session_store: Dict[str, SessionKey] = {}
exchange: Optional[HybridKeyExchange] = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global exchange
    exchange = HybridKeyExchange()
    LOGGER.info("Quantum-safe crypto service initialized")
    yield
    LOGGER.info("Quantum-safe crypto service shutting down")


app = FastAPI(
    title="Quantum-Safe Cryptography API",
    description="Post-quantum cryptography service with hybrid key exchange",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class GenerateKeyRequest(BaseModel):
    """Request to generate a keypair."""
    algorithm: str = Field(default="Kyber768", description="KEM algorithm")
    key_name: Optional[str] = None


class KeyPairResponse(BaseModel):
    """Response containing key information."""
    key_id: str
    algorithm_pqc: str
    algorithm_classical: str
    public_key_pqc: str  # Base64 encoded
    public_key_classical: str  # Base64 encoded
    created_at: str


class EncapsulateRequest(BaseModel):
    """Request to encapsulate a secret."""
    recipient_pqc_public: str  # Base64 encoded
    recipient_classical_public: str  # Base64 encoded


class EncapsulateResponse(BaseModel):
    """Encapsulation response."""
    pqc_ciphertext: str  # Base64 encoded
    classical_public: str  # Base64 encoded
    shared_secret: str  # Base64 encoded (for demo only, don't return in production!)


class DecapsulateRequest(BaseModel):
    """Request to decapsulate."""
    key_id: str
    pqc_ciphertext: str  # Base64 encoded
    classical_public: str  # Base64 encoded


class SignRequest(BaseModel):
    """Request to sign a message."""
    key_id: str
    message: str  # Base64 encoded
    algorithm: str = "Dilithium3"


class SignResponse(BaseModel):
    """Signature response."""
    signature: str  # Base64 encoded
    algorithm: str


class VerifyRequest(BaseModel):
    """Request to verify a signature."""
    public_key: str  # Base64 encoded
    message: str  # Base64 encoded
    signature: str  # Base64 encoded
    algorithm: str = "Dilithium3"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    liboqs_available: bool
    uptime_seconds: float
    keys_stored: int


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        liboqs_available=LIBOQS_AVAILABLE,
        uptime_seconds=time.time() - start_time,
        keys_stored=len(key_store),
    )


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/algorithms")
async def list_algorithms():
    """List supported algorithms."""
    return {
        "kem_algorithms": [
            {"name": alg.value, "nist_level": _get_nist_level(alg)}
            for alg in KEMAlgorithm
        ],
        "signature_algorithms": [
            {"name": alg.value}
            for alg in SignatureAlgorithm
        ],
        "liboqs_available": LIBOQS_AVAILABLE,
    }


@app.post("/keys/generate", response_model=KeyPairResponse)
async def generate_keypair(request: GenerateKeyRequest):
    """Generate a new hybrid keypair."""
    start = time.time()

    try:
        algorithm = KEMAlgorithm(request.algorithm)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid algorithm: {request.algorithm}")

    hybrid_exchange = HybridKeyExchange(pqc_algorithm=algorithm)
    keypair = hybrid_exchange.generate_keypair()

    # Store keypair
    key_store[keypair.key_id] = keypair

    KEYPAIRS_GENERATED.labels(algorithm=request.algorithm).inc()
    OPERATION_LATENCY.labels(operation="generate_keypair").observe(time.time() - start)

    return KeyPairResponse(
        key_id=keypair.key_id,
        algorithm_pqc=keypair.algorithm_pqc,
        algorithm_classical=keypair.algorithm_classical,
        public_key_pqc=base64.b64encode(keypair.pqc_keypair.public_key).decode(),
        public_key_classical=base64.b64encode(keypair.classical_public).decode(),
        created_at=keypair.created_at.isoformat(),
    )


@app.get("/keys/{key_id}", response_model=KeyPairResponse)
async def get_key(key_id: str):
    """Get public key information."""
    if key_id not in key_store:
        raise HTTPException(status_code=404, detail="Key not found")

    keypair = key_store[key_id]

    return KeyPairResponse(
        key_id=keypair.key_id,
        algorithm_pqc=keypair.algorithm_pqc,
        algorithm_classical=keypair.algorithm_classical,
        public_key_pqc=base64.b64encode(keypair.pqc_keypair.public_key).decode(),
        public_key_classical=base64.b64encode(keypair.classical_public).decode(),
        created_at=keypair.created_at.isoformat(),
    )


@app.get("/keys")
async def list_keys():
    """List all stored keys."""
    return {
        "keys": [
            {
                "key_id": kp.key_id,
                "algorithm_pqc": kp.algorithm_pqc,
                "created_at": kp.created_at.isoformat(),
            }
            for kp in key_store.values()
        ]
    }


@app.delete("/keys/{key_id}")
async def delete_key(key_id: str):
    """Delete a stored key."""
    if key_id not in key_store:
        raise HTTPException(status_code=404, detail="Key not found")

    del key_store[key_id]
    return {"deleted": True}


@app.post("/encapsulate", response_model=EncapsulateResponse)
async def encapsulate(request: EncapsulateRequest):
    """Encapsulate a shared secret for a recipient."""
    start = time.time()

    try:
        pqc_public = base64.b64decode(request.recipient_pqc_public)
        classical_public = base64.b64decode(request.recipient_classical_public)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    encap, shared_secret = exchange.encapsulate(pqc_public, classical_public)

    ENCAPSULATIONS.labels(algorithm=exchange.pqc_provider.algorithm).inc()
    OPERATION_LATENCY.labels(operation="encapsulate").observe(time.time() - start)

    return EncapsulateResponse(
        pqc_ciphertext=base64.b64encode(encap.pqc_ciphertext).decode(),
        classical_public=base64.b64encode(encap.classical_public).decode(),
        shared_secret=base64.b64encode(shared_secret).decode(),
    )


@app.post("/decapsulate")
async def decapsulate(request: DecapsulateRequest):
    """Decapsulate to recover shared secret."""
    start = time.time()

    if request.key_id not in key_store:
        raise HTTPException(status_code=404, detail="Key not found")

    keypair = key_store[request.key_id]

    try:
        pqc_ciphertext = base64.b64decode(request.pqc_ciphertext)
        classical_public = base64.b64decode(request.classical_public)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    from .hybrid_exchange import HybridEncapsulation

    encap = HybridEncapsulation(
        pqc_ciphertext=pqc_ciphertext,
        classical_public=classical_public,
        combined_hash=b"",  # Will be recalculated
    )

    shared_secret = exchange.decapsulate(keypair, encap)

    OPERATION_LATENCY.labels(operation="decapsulate").observe(time.time() - start)

    return {
        "shared_secret": base64.b64encode(shared_secret).decode(),
    }


@app.post("/sign", response_model=SignResponse)
async def sign_message(request: SignRequest):
    """Sign a message."""
    start = time.time()

    try:
        algorithm = SignatureAlgorithm(request.algorithm)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid algorithm: {request.algorithm}")

    if request.key_id not in key_store:
        raise HTTPException(status_code=404, detail="Key not found")

    try:
        message = base64.b64decode(request.message)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    sig_provider = create_signature_provider(algorithm)
    sig_keypair = sig_provider.generate_keypair()
    result = sig_provider.sign(sig_keypair.secret_key, message)

    SIGNATURES.labels(algorithm=request.algorithm).inc()
    OPERATION_LATENCY.labels(operation="sign").observe(time.time() - start)

    return SignResponse(
        signature=base64.b64encode(result.signature).decode(),
        algorithm=sig_provider.algorithm,
    )


@app.post("/verify")
async def verify_signature(request: VerifyRequest):
    """Verify a signature."""
    start = time.time()

    try:
        algorithm = SignatureAlgorithm(request.algorithm)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid algorithm: {request.algorithm}")

    try:
        public_key = base64.b64decode(request.public_key)
        message = base64.b64decode(request.message)
        signature = base64.b64decode(request.signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    sig_provider = create_signature_provider(algorithm)
    is_valid = sig_provider.verify(public_key, message, signature)

    OPERATION_LATENCY.labels(operation="verify").observe(time.time() - start)

    return {"valid": is_valid}


def _get_nist_level(algorithm: KEMAlgorithm) -> int:
    """Get NIST security level for algorithm."""
    levels = {
        KEMAlgorithm.KYBER512: 1,
        KEMAlgorithm.KYBER768: 3,
        KEMAlgorithm.KYBER1024: 5,
    }
    return levels.get(algorithm, 0)
