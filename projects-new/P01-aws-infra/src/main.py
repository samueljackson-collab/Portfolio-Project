"""FastAPI application exposing AWS automation helpers."""

from __future__ import annotations

import time
from typing import Annotated, Dict, List

import structlog
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from src.config import Settings, get_settings
from src.metrics import metrics_endpoint, metrics_middleware
from src.security import apply_security_headers, verify_api_key
from src.services import AWSResourceService, AWSServiceError

structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger(__name__)

app = FastAPI(title="AWS Infrastructure Automation API", version="1.1.0")
app.middleware("http")(metrics_middleware)


class PublishMetricPayload(BaseModel):
    metric_name: str = Field(..., description="Custom metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(default="Count", description="Metric unit")


class SecurityPosture(BaseModel):
    owasp_top_10_controls: str
    cis_benchmark_status: str
    dependency_scanning: str
    secrets_management: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    timestamp: float


ApiKeyDep = Annotated[str, Depends(verify_api_key)]


def get_aws_service() -> AWSResourceService:
    settings = get_settings()
    return AWSResourceService(region=settings.aws_region)


@app.middleware("http")
async def secure_headers_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    for key, value in apply_security_headers({}).items():
        response.headers.setdefault(key, value)
    return response


@app.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Basic health endpoint used by load balancers and uptime checks."""

    logger.info("health_check", environment=settings.environment)
    return HealthResponse(status="healthy", environment=settings.environment, timestamp=time.time())


@app.get("/aws/s3/buckets")
def s3_buckets(
    _: ApiKeyDep,
    service: AWSResourceService = Depends(get_aws_service),
) -> Dict[str, List[Dict[str, str]]]:
    """Return S3 buckets to demonstrate AWS SDK usage."""

    buckets = service.list_s3_buckets()
    return {"buckets": buckets}


@app.get("/security/posture", response_model=SecurityPosture)
def security_posture(_: ApiKeyDep) -> SecurityPosture:
    """Summarize currently implemented and roadmap security controls."""

    return SecurityPosture(
        owasp_top_10_controls="Implemented for authn/authz + input validation; remaining controls tracked in backlog.",
        cis_benchmark_status="Guardrails automated for IAM/logging; full CIS Level 2 audit scheduled in roadmap.",
        dependency_scanning="Automated via CI safety checks and SBOM export.",
        secrets_management="AWS Secrets Manager metadata surfaced via /aws endpoints.",
    )


@app.post("/aws/metrics/publish")
def publish_metric(
    payload: PublishMetricPayload,
    _: ApiKeyDep,
    service: AWSResourceService = Depends(get_aws_service),
):
    """Publish a custom CloudWatch metric to validate telemetry integration."""

    try:
        return service.publish_custom_metric(payload.metric_name, payload.value, payload.unit)
    except AWSServiceError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@app.get("/metrics")
def prometheus_metrics():
    """Expose application metrics for Prometheus scraping."""

    payload, content_type = metrics_endpoint()
    return PlainTextResponse(content=payload.decode("utf-8"), media_type=content_type)


@app.get("/secrets/{secret_name}")
def secret_metadata(
    secret_name: str,
    _: ApiKeyDep,
    service: AWSResourceService = Depends(get_aws_service),
):
    """Surface Secrets Manager metadata without revealing the secret value."""

    try:
        result = service.describe_secret(secret_name)
        return JSONResponse(content=result)
    except AWSServiceError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
