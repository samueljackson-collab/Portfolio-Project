"""FastAPI REST API for Quantum Portfolio Optimizer."""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .config import AppConfig, SolverType
from .classical_solvers import Asset, OptimizationResult, create_solver
from .portfolio_optimizer import optimize_portfolio

LOGGER = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "quantum_optimizer_requests_total",
    "Total optimization requests",
    ["solver_type", "status"]
)
REQUEST_LATENCY = Histogram(
    "quantum_optimizer_request_duration_seconds",
    "Request latency in seconds",
    ["solver_type"]
)
SHARPE_RATIO = Histogram(
    "quantum_optimizer_sharpe_ratio",
    "Distribution of Sharpe ratios from optimizations"
)

# In-memory job store
jobs: Dict[str, dict] = {}
config: Optional[AppConfig] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global config
    config = AppConfig.from_env()
    LOGGER.info("Quantum Portfolio Optimizer started")
    yield
    LOGGER.info("Quantum Portfolio Optimizer shutting down")


app = FastAPI(
    title="Quantum Portfolio Optimizer API",
    description="REST API for quantum-assisted portfolio optimization",
    version="1.0.0",
    lifespan=lifespan,
)


class AssetInput(BaseModel):
    """Input model for a single asset."""
    symbol: str = Field(..., description="Asset ticker symbol")
    expected_return: float = Field(..., description="Expected annual return (decimal)")
    volatility: float = Field(..., ge=0, description="Asset volatility (std dev)")
    sector: str = Field(default="general", description="Asset sector classification")

    @validator("expected_return")
    def validate_return(cls, v):
        if v < -1 or v > 10:
            raise ValueError("Expected return must be between -100% and 1000%")
        return v


class ConstraintsInput(BaseModel):
    """Portfolio constraints input."""
    min_assets: int = Field(default=3, ge=1)
    max_assets: int = Field(default=20, le=100)
    min_weight: float = Field(default=0.01, ge=0, le=1)
    max_weight: float = Field(default=0.40, ge=0, le=1)
    target_return: Optional[float] = None
    max_risk: Optional[float] = None


class OptimizationRequest(BaseModel):
    """Request model for portfolio optimization."""
    assets: List[AssetInput] = Field(..., min_items=2)
    covariance_matrix: Optional[List[List[float]]] = None
    constraints: ConstraintsInput = Field(default_factory=ConstraintsInput)
    solver_type: str = Field(default="hybrid")
    risk_free_rate: float = Field(default=0.02)
    use_quantum: bool = Field(default=False)

    @validator("covariance_matrix")
    def validate_cov_matrix(cls, v, values):
        if v is not None:
            n = len(values.get("assets", []))
            if len(v) != n or any(len(row) != n for row in v):
                raise ValueError(f"Covariance matrix must be {n}x{n}")
        return v


class OptimizationResponse(BaseModel):
    """Response model for optimization result."""
    job_id: str
    status: str
    weights: Optional[Dict[str, float]] = None
    expected_return: Optional[float] = None
    risk: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    solver_type: Optional[str] = None
    iterations: Optional[int] = None
    converged: Optional[bool] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    quantum_available: bool
    uptime_seconds: float


start_time = time.time()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    try:
        from qiskit import Aer
        quantum_available = Aer is not None
    except ImportError:
        quantum_available = False

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        quantum_available=quantum_available,
        uptime_seconds=time.time() - start_time,
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def run_optimization(job_id: str, request: OptimizationRequest):
    """Background task to run optimization."""
    global config
    start = time.time()

    try:
        assets = [
            Asset(
                symbol=a.symbol,
                expected_return=a.expected_return,
                volatility=a.volatility,
                sector=a.sector,
            )
            for a in request.assets
        ]

        # Generate covariance matrix if not provided
        if request.covariance_matrix:
            cov_matrix = np.array(request.covariance_matrix)
        else:
            # Generate from volatilities with correlation
            n = len(assets)
            volatilities = np.array([a.volatility for a in assets])
            correlation = np.eye(n) * 0.5 + np.ones((n, n)) * 0.5
            cov_matrix = np.outer(volatilities, volatilities) * correlation

        # Update config with request parameters
        solver_type = SolverType(request.solver_type)
        config.solver_type = solver_type
        config.classical.solver_type = solver_type

        # Create and run solver
        solver = create_solver(config.classical, config.constraints)
        result = solver.optimize(assets, cov_matrix, request.risk_free_rate)

        jobs[job_id].update({
            "status": "completed",
            "weights": result.weights,
            "expected_return": result.expected_return,
            "risk": result.risk,
            "sharpe_ratio": result.sharpe_ratio,
            "solver_type": result.solver_type,
            "iterations": result.iterations,
            "converged": result.converged,
            "completed_at": datetime.utcnow().isoformat(),
        })

        # Record metrics
        duration = time.time() - start
        REQUEST_COUNT.labels(solver_type=request.solver_type, status="success").inc()
        REQUEST_LATENCY.labels(solver_type=request.solver_type).observe(duration)
        SHARPE_RATIO.observe(result.sharpe_ratio)

        LOGGER.info(
            "Optimization completed",
            extra={
                "job_id": job_id,
                "sharpe_ratio": result.sharpe_ratio,
                "duration": duration,
            },
        )

    except Exception as e:
        LOGGER.exception("Optimization failed", extra={"job_id": job_id})
        REQUEST_COUNT.labels(solver_type=request.solver_type, status="error").inc()
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat(),
        })


@app.post("/optimize", response_model=OptimizationResponse)
async def submit_optimization(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
):
    """Submit a portfolio optimization job."""
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(run_optimization, job_id, request)

    return OptimizationResponse(
        job_id=job_id,
        status="pending",
        created_at=jobs[job_id]["created_at"],
    )


@app.get("/optimize/{job_id}", response_model=OptimizationResponse)
async def get_optimization_result(job_id: str):
    """Get the result of an optimization job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return OptimizationResponse(**job)


@app.get("/jobs", response_model=List[OptimizationResponse])
async def list_jobs(limit: int = 10, status: Optional[str] = None):
    """List recent optimization jobs."""
    job_list = list(jobs.values())

    if status:
        job_list = [j for j in job_list if j.get("status") == status]

    job_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [OptimizationResponse(**j) for j in job_list[:limit]]


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete an optimization job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]
    return {"message": "Job deleted"}


@app.get("/solvers")
async def list_solvers():
    """List available solvers."""
    return {
        "solvers": [
            {
                "name": "simulated_annealing",
                "description": "Classical simulated annealing optimizer",
                "quantum_required": False,
            },
            {
                "name": "genetic_algorithm",
                "description": "Genetic algorithm for portfolio optimization",
                "quantum_required": False,
            },
            {
                "name": "hybrid",
                "description": "Hybrid solver combining multiple approaches",
                "quantum_required": False,
            },
            {
                "name": "quantum_vqe",
                "description": "Variational Quantum Eigensolver",
                "quantum_required": True,
            },
            {
                "name": "quantum_qaoa",
                "description": "Quantum Approximate Optimization Algorithm",
                "quantum_required": True,
            },
        ]
    }
