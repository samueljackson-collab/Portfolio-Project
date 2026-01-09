"""FastAPI REST API for Blockchain Oracle Service."""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .oracle_service import (
    OracleService,
    OracleRequest,
    MetricType,
    create_oracle_service,
)

LOGGER = logging.getLogger(__name__)

# Prometheus metrics
REQUESTS_TOTAL = Counter(
    "oracle_requests_total",
    "Total oracle requests",
    ["metric_type", "status"]
)
REQUEST_LATENCY = Histogram(
    "oracle_request_latency_seconds",
    "Request latency in seconds",
    ["metric_type"]
)
SIGNATURES_GENERATED = Counter(
    "oracle_signatures_generated_total",
    "Total signatures generated"
)

oracle_service: Optional[OracleService] = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global oracle_service
    oracle_service = create_oracle_service()
    LOGGER.info("Oracle service initialized")
    yield
    LOGGER.info("Oracle service shutting down")


app = FastAPI(
    title="Blockchain Oracle Service",
    description="Chainlink-compatible oracle for portfolio metrics",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class OracleRequestModel(BaseModel):
    """Chainlink-compatible oracle request."""
    id: str = Field(..., description="Job run ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Request parameters")


class OracleResponseModel(BaseModel):
    """Chainlink-compatible oracle response."""
    jobRunID: str
    data: Dict[str, Any]
    result: int
    statusCode: int


class MetricRequestModel(BaseModel):
    """Request for a specific metric."""
    metric_type: str = Field(..., description="Type of metric to fetch")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    callback_address: Optional[str] = None


class SignedResponseModel(BaseModel):
    """Signed oracle response."""
    request_id: str
    value: int
    timestamp: int
    signature: str
    signer: str
    raw_data: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    signer_address: str


# Chainlink External Adapter Endpoint
@app.post("/", response_model=OracleResponseModel)
async def chainlink_adapter(request: OracleRequestModel):
    """
    Chainlink external adapter endpoint.
    Compatible with Chainlink job specifications.
    """
    start = time.time()
    job_id = request.id

    try:
        # Parse metric type from request
        metric_type_str = request.data.get("metric", "portfolio_value")
        try:
            metric_type = MetricType(metric_type_str)
        except ValueError:
            metric_type = MetricType.CUSTOM

        # Create oracle request
        oracle_request = OracleRequest(
            request_id=job_id,
            metric_type=metric_type,
            parameters=request.data,
        )

        # Process request
        response = await oracle_service.process_request(oracle_request)

        # Record metrics
        duration = time.time() - start
        REQUESTS_TOTAL.labels(metric_type=metric_type_str, status="success").inc()
        REQUEST_LATENCY.labels(metric_type=metric_type_str).observe(duration)
        SIGNATURES_GENERATED.inc()

        return OracleResponseModel(
            jobRunID=job_id,
            data={
                "result": response.value,
                "signature": response.signature,
                "signer": response.signer,
                "timestamp": response.timestamp,
            },
            result=response.value,
            statusCode=200,
        )

    except Exception as e:
        LOGGER.exception(f"Oracle request failed: {e}")
        REQUESTS_TOTAL.labels(metric_type="unknown", status="error").inc()

        return OracleResponseModel(
            jobRunID=job_id,
            data={"error": str(e)},
            result=0,
            statusCode=500,
        )


@app.post("/metrics", response_model=SignedResponseModel)
async def get_signed_metric(request: MetricRequestModel):
    """Get a signed metric value."""
    start = time.time()

    try:
        metric_type = MetricType(request.metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {request.metric_type}")

    request_id = f"0x{uuid.uuid4().hex}"

    oracle_request = OracleRequest(
        request_id=request_id,
        metric_type=metric_type,
        parameters=request.parameters,
        callback_address=request.callback_address,
    )

    try:
        response = await oracle_service.process_request(oracle_request)

        duration = time.time() - start
        REQUESTS_TOTAL.labels(metric_type=request.metric_type, status="success").inc()
        REQUEST_LATENCY.labels(metric_type=request.metric_type).observe(duration)
        SIGNATURES_GENERATED.inc()

        return SignedResponseModel(
            request_id=response.request_id,
            value=response.value,
            timestamp=response.timestamp,
            signature=response.signature,
            signer=response.signer,
            raw_data=response.raw_data,
        )

    except Exception as e:
        REQUESTS_TOTAL.labels(metric_type=request.metric_type, status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/types")
async def list_metric_types():
    """List available metric types."""
    return {
        "metric_types": [
            {"name": mt.value, "description": mt.name.replace("_", " ").title()}
            for mt in MetricType
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time() - start_time,
        signer_address=oracle_service.signer.address if oracle_service else "not_initialized",
    )


@app.get("/prometheus")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/signer")
async def get_signer_info():
    """Get oracle signer information."""
    if not oracle_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return {
        "address": oracle_service.signer.address,
        "message": "Use this address to verify oracle signatures on-chain",
    }


@app.post("/verify")
async def verify_signature(
    request_id: str,
    value: int,
    timestamp: int,
    signature: str,
):
    """Verify an oracle signature."""
    if not oracle_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        is_valid = oracle_service.signer.verify_signature(
            request_id, value, timestamp, signature
        )
        return {"valid": is_valid, "signer": oracle_service.signer.address}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {e}")
