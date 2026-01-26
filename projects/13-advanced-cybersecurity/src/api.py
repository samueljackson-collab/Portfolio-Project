"""FastAPI REST API for SOAR Engine."""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .soar_engine import Alert, SoarEngine
from .enrichment_adapters import (
    EnrichmentAggregator,
    EnrichmentCache,
    VirusTotalAdapter,
    AbuseIPDBAdapter,
)
from .playbook_engine import PlaybookEngine, Playbook, PlaybookStatus

LOGGER = logging.getLogger(__name__)

# Prometheus metrics
ALERTS_PROCESSED = Counter(
    "soar_alerts_processed_total",
    "Total alerts processed",
    ["severity", "status"]
)
ENRICHMENT_REQUESTS = Counter(
    "soar_enrichment_requests_total",
    "Total enrichment requests",
    ["indicator_type", "source"]
)
PLAYBOOK_EXECUTIONS = Counter(
    "soar_playbook_executions_total",
    "Total playbook executions",
    ["playbook", "status"]
)
ALERT_PROCESSING_TIME = Histogram(
    "soar_alert_processing_seconds",
    "Alert processing time in seconds"
)

# Global instances
soar_engine: Optional[SoarEngine] = None
enrichment_aggregator: Optional[EnrichmentAggregator] = None
playbook_engine: Optional[PlaybookEngine] = None

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global soar_engine, enrichment_aggregator, playbook_engine

    # Initialize SOAR engine
    soar_engine = SoarEngine()

    # Initialize enrichment adapters
    cache = EnrichmentCache(ttl_seconds=3600)
    adapters = []

    vt_key = os.environ.get("VIRUSTOTAL_API_KEY")
    if vt_key:
        adapters.append(VirusTotalAdapter(api_key=vt_key, cache=cache))

    abuseipdb_key = os.environ.get("ABUSEIPDB_API_KEY")
    if abuseipdb_key:
        adapters.append(AbuseIPDBAdapter(api_key=abuseipdb_key, cache=cache))

    enrichment_aggregator = EnrichmentAggregator(adapters) if adapters else None

    # Initialize playbook engine
    playbook_engine = PlaybookEngine()

    # Load playbooks from directory
    playbooks_dir = os.environ.get("PLAYBOOKS_DIR", "/app/playbooks")
    if os.path.isdir(playbooks_dir):
        for filename in os.listdir(playbooks_dir):
            if filename.endswith((".yaml", ".yml")):
                try:
                    playbook_engine.load_playbook(os.path.join(playbooks_dir, filename))
                    LOGGER.info(f"Loaded playbook: {filename}")
                except Exception as e:
                    LOGGER.error(f"Failed to load playbook {filename}: {e}")

    LOGGER.info("SOAR Engine started")
    yield
    LOGGER.info("SOAR Engine shutting down")


app = FastAPI(
    title="SOAR Engine API",
    description="Security Orchestration, Automation and Response API",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class AlertInput(BaseModel):
    """Alert input model."""
    id: str = Field(..., description="Alert ID")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    source_ip: str = Field(..., description="Source IP address")
    asset_id: str = Field(..., description="Target asset ID")
    description: str = Field(..., description="Alert description")
    tags: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class AlertResponse(BaseModel):
    """Alert processing response."""
    alert_id: str
    status: str
    risk_score: float
    enrichment: Optional[Dict[str, Any]] = None
    actions_taken: List[str] = Field(default_factory=list)
    processing_time_ms: float


class EnrichmentRequest(BaseModel):
    """Enrichment request model."""
    indicator: str = Field(..., description="Indicator to enrich (IP, domain, hash)")
    indicator_type: str = Field(..., description="Type: ip, domain, hash")


class EnrichmentResponse(BaseModel):
    """Enrichment response model."""
    indicator: str
    indicator_type: str
    is_malicious: bool
    confidence: float
    sources: List[str]
    details: Dict[str, Any]


class PlaybookInput(BaseModel):
    """Playbook input model."""
    content: str = Field(..., description="Playbook YAML content")


class PlaybookExecutionRequest(BaseModel):
    """Playbook execution request."""
    playbook_name: str
    context: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False


class PlaybookExecutionResponse(BaseModel):
    """Playbook execution response."""
    execution_id: str
    playbook_name: str
    status: str
    steps_completed: int
    steps_total: int
    started_at: str
    completed_at: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    enrichment_sources: List[str]
    playbooks_loaded: int


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    enrichment_sources = []
    if enrichment_aggregator:
        enrichment_sources = [a.source_name for a in enrichment_aggregator.adapters]

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time() - start_time,
        enrichment_sources=enrichment_sources,
        playbooks_loaded=len(playbook_engine.list_playbooks()) if playbook_engine else 0,
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/alerts", response_model=AlertResponse)
async def process_alert(alert_input: AlertInput, background_tasks: BackgroundTasks):
    """Process a security alert."""
    start = time.time()

    alert = Alert(
        id=alert_input.id,
        severity=alert_input.severity,
        source_ip=alert_input.source_ip,
        asset_id=alert_input.asset_id,
        description=alert_input.description,
        tags=alert_input.tags,
    )

    # Enrich alert
    enrichment = None
    if enrichment_aggregator:
        try:
            results = await enrichment_aggregator.enrich_ip(alert.source_ip)
            enrichment = enrichment_aggregator.aggregate_verdict(results)
            ENRICHMENT_REQUESTS.labels(indicator_type="ip", source="aggregated").inc()
        except Exception as e:
            LOGGER.error(f"Enrichment failed: {e}")

    # Calculate risk score
    context = soar_engine._enrich(alert)
    if enrichment:
        context["threat_confidence"] = enrichment.get("confidence", 0)
    risk_score = soar_engine._score(context)

    # Determine actions
    actions_taken = []
    if risk_score >= 0.8:
        actions_taken.append("isolate_host")
        actions_taken.append("block_ip")
    if risk_score >= 0.6:
        actions_taken.append("create_ticket")
    actions_taken.append("log_alert")

    # Execute relevant playbook in background
    if playbook_engine and risk_score >= 0.7:
        playbook = playbook_engine.get_playbook("high-risk-response")
        if playbook:
            background_tasks.add_task(
                playbook_engine.execute,
                playbook,
                {"alert_id": alert.id, "source_ip": alert.source_ip, "asset_id": alert.asset_id},
            )

    processing_time = (time.time() - start) * 1000

    # Record metrics
    ALERTS_PROCESSED.labels(severity=alert.severity, status="processed").inc()
    ALERT_PROCESSING_TIME.observe(processing_time / 1000)

    return AlertResponse(
        alert_id=alert.id,
        status="processed",
        risk_score=risk_score,
        enrichment=enrichment,
        actions_taken=actions_taken,
        processing_time_ms=processing_time,
    )


@app.post("/alerts/batch", response_model=List[AlertResponse])
async def process_alerts_batch(alerts: List[AlertInput]):
    """Process multiple alerts in batch."""
    responses = []
    for alert_input in alerts:
        # Simplified batch processing
        alert = Alert(
            id=alert_input.id,
            severity=alert_input.severity,
            source_ip=alert_input.source_ip,
            asset_id=alert_input.asset_id,
            description=alert_input.description,
            tags=alert_input.tags,
        )

        context = soar_engine._enrich(alert)
        risk_score = soar_engine._score(context)

        responses.append(AlertResponse(
            alert_id=alert.id,
            status="processed",
            risk_score=risk_score,
            actions_taken=["log_alert"],
            processing_time_ms=0,
        ))

        ALERTS_PROCESSED.labels(severity=alert.severity, status="processed").inc()

    return responses


@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_indicator(request: EnrichmentRequest):
    """Enrich a security indicator."""
    if not enrichment_aggregator:
        raise HTTPException(status_code=503, detail="Enrichment services not configured")

    indicator_type = request.indicator_type.lower()

    if indicator_type == "ip":
        results = await enrichment_aggregator.enrich_ip(request.indicator)
    elif indicator_type == "domain":
        results = await enrichment_aggregator.enrich_domain(request.indicator)
    elif indicator_type == "hash":
        results = await enrichment_aggregator.enrich_hash(request.indicator)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid indicator type: {indicator_type}")

    verdict = enrichment_aggregator.aggregate_verdict(results)

    for source in verdict.get("sources", []):
        ENRICHMENT_REQUESTS.labels(indicator_type=indicator_type, source=source).inc()

    return EnrichmentResponse(
        indicator=request.indicator,
        indicator_type=indicator_type,
        is_malicious=verdict.get("is_malicious", False),
        confidence=verdict.get("confidence", 0),
        sources=verdict.get("sources", []),
        details=verdict,
    )


@app.get("/playbooks", response_model=List[str])
async def list_playbooks():
    """List available playbooks."""
    if not playbook_engine:
        return []
    return playbook_engine.list_playbooks()


@app.post("/playbooks")
async def create_playbook(playbook_input: PlaybookInput):
    """Create a new playbook from YAML."""
    if not playbook_engine:
        raise HTTPException(status_code=503, detail="Playbook engine not initialized")

    try:
        playbook = playbook_engine.load_playbook_from_string(playbook_input.content)
        return {"name": playbook.name, "steps": len(playbook.steps)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid playbook: {e}")


@app.get("/playbooks/{name}")
async def get_playbook(name: str):
    """Get playbook details."""
    if not playbook_engine:
        raise HTTPException(status_code=503, detail="Playbook engine not initialized")

    playbook = playbook_engine.get_playbook(name)
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")

    return {
        "name": playbook.name,
        "description": playbook.description,
        "version": playbook.version,
        "enabled": playbook.enabled,
        "steps": [
            {"id": s.id, "name": s.name, "action": s.action}
            for s in playbook.steps
        ],
    }


@app.post("/playbooks/execute", response_model=PlaybookExecutionResponse)
async def execute_playbook(request: PlaybookExecutionRequest):
    """Execute a playbook."""
    if not playbook_engine:
        raise HTTPException(status_code=503, detail="Playbook engine not initialized")

    playbook = playbook_engine.get_playbook(request.playbook_name)
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")

    execution = await playbook_engine.execute(
        playbook,
        request.context,
        dry_run=request.dry_run,
    )

    PLAYBOOK_EXECUTIONS.labels(
        playbook=request.playbook_name,
        status=execution.status.value,
    ).inc()

    return PlaybookExecutionResponse(
        execution_id=execution.execution_id,
        playbook_name=execution.playbook_name,
        status=execution.status.value,
        steps_completed=sum(1 for s in execution.steps if s.status.value == "success"),
        steps_total=len(execution.steps),
        started_at=execution.started_at.isoformat(),
        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
    )


@app.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get playbook execution details."""
    if not playbook_engine:
        raise HTTPException(status_code=503, detail="Playbook engine not initialized")

    execution = playbook_engine.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution.to_dict()


@app.get("/executions")
async def list_executions(limit: int = 10):
    """List recent playbook executions."""
    if not playbook_engine:
        return []

    executions = playbook_engine.list_executions(limit)
    return [e.to_dict() for e in executions]


@app.get("/actions")
async def list_actions():
    """List available playbook actions."""
    if not playbook_engine:
        return []
    return playbook_engine.registry.list_actions()
