"""
Portfolio Staking Platform - REST API.

FastAPI application providing REST endpoints for:
- Staking operations (stake, withdraw, claim)
- Position queries
- Protocol statistics
- Event history
"""

import os
import logging
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .blockchain_service import BlockchainService, EventIndexer, StakeInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID = int(os.getenv("CHAIN_ID", "31337"))
STAKING_CONTRACT = os.getenv("STAKING_CONTRACT_ADDRESS")
STAKING_TOKEN = os.getenv("STAKING_TOKEN_ADDRESS")
REWARD_TOKEN = os.getenv("REWARD_TOKEN_ADDRESS")

# Prometheus metrics
STAKE_OPERATIONS = Counter(
    "stake_operations_total",
    "Total staking operations",
    ["operation"]
)
TOTAL_STAKED_GAUGE = Gauge(
    "total_staked",
    "Total amount staked in the protocol"
)
API_ERRORS = Counter(
    "api_errors_total",
    "Total API errors",
    ["endpoint"]
)

# Global service instances
blockchain_service: Optional[BlockchainService] = None
event_indexer: Optional[EventIndexer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global blockchain_service, event_indexer

    # Initialize blockchain service
    blockchain_service = BlockchainService(
        rpc_url=RPC_URL,
        private_key=PRIVATE_KEY,
        chain_id=CHAIN_ID
    )

    # Setup contracts if addresses provided
    if all([STAKING_CONTRACT, STAKING_TOKEN, REWARD_TOKEN]):
        try:
            blockchain_service.setup_staking_contract(
                STAKING_CONTRACT,
                STAKING_TOKEN,
                REWARD_TOKEN
            )
            event_indexer = EventIndexer(blockchain_service)
            logger.info("Blockchain service initialized with contracts")
        except Exception as e:
            logger.warning(f"Could not setup contracts: {e}")
    else:
        logger.info("Blockchain service initialized (no contracts configured)")

    yield

    # Cleanup
    logger.info("Shutting down blockchain service")


app = FastAPI(
    title="Portfolio Staking Platform API",
    description="REST API for Portfolio Staking smart contract interactions",
    version="1.0.0",
    lifespan=lifespan
)


# ==================== Request/Response Models ====================

class StakeRequest(BaseModel):
    """Request to stake tokens."""
    amount: int = Field(..., gt=0, description="Amount to stake in token units")


class WithdrawRequest(BaseModel):
    """Request to withdraw tokens."""
    amount: int = Field(..., gt=0, description="Amount to withdraw in token units")


class ApproveRequest(BaseModel):
    """Request to approve token spending."""
    amount: int = Field(..., gt=0, description="Amount to approve in token units")


class TransactionResponse(BaseModel):
    """Response for transaction operations."""
    success: bool
    tx_hash: str
    block_number: int
    gas_used: int
    events: List[dict] = []


class StakeInfoResponse(BaseModel):
    """Response with staking information."""
    address: str
    balance: int
    pending_rewards: int
    reward_debt: int
    last_updated: int


class ProtocolStatsResponse(BaseModel):
    """Response with protocol statistics."""
    total_staked: int
    reward_rate: int
    total_users: int
    total_rewards_distributed: int
    block_number: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    connected: bool
    block_number: int
    contracts_configured: bool


# ==================== Health Endpoints ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if blockchain_service and blockchain_service.is_connected else "degraded",
        connected=blockchain_service.is_connected if blockchain_service else False,
        block_number=blockchain_service.block_number if blockchain_service and blockchain_service.is_connected else 0,
        contracts_configured=blockchain_service.staking_contract is not None if blockchain_service else False
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Update gauges
    if blockchain_service and blockchain_service.staking_contract:
        try:
            total = blockchain_service.get_total_staked()
            TOTAL_STAKED_GAUGE.set(total)
        except Exception:
            pass

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ==================== Staking Endpoints ====================

@app.post("/stake", response_model=TransactionResponse)
async def stake_tokens(request: StakeRequest):
    """
    Stake tokens in the contract.

    Requires prior approval for the staking contract to spend tokens.
    """
    if not blockchain_service or not blockchain_service.staking_contract:
        API_ERRORS.labels(endpoint="stake").inc()
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        result = blockchain_service.stake(request.amount)
        STAKE_OPERATIONS.labels(operation="stake").inc()

        return TransactionResponse(
            success=result.status,
            tx_hash=result.tx_hash,
            block_number=result.block_number,
            gas_used=result.gas_used,
            events=result.events
        )
    except Exception as e:
        API_ERRORS.labels(endpoint="stake").inc()
        logger.error(f"Stake error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/withdraw", response_model=TransactionResponse)
async def withdraw_tokens(request: WithdrawRequest):
    """Withdraw staked tokens."""
    if not blockchain_service or not blockchain_service.staking_contract:
        API_ERRORS.labels(endpoint="withdraw").inc()
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        result = blockchain_service.withdraw(request.amount)
        STAKE_OPERATIONS.labels(operation="withdraw").inc()

        return TransactionResponse(
            success=result.status,
            tx_hash=result.tx_hash,
            block_number=result.block_number,
            gas_used=result.gas_used,
            events=result.events
        )
    except Exception as e:
        API_ERRORS.labels(endpoint="withdraw").inc()
        logger.error(f"Withdraw error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/claim", response_model=TransactionResponse)
async def claim_rewards():
    """Claim pending rewards."""
    if not blockchain_service or not blockchain_service.staking_contract:
        API_ERRORS.labels(endpoint="claim").inc()
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        result = blockchain_service.claim_rewards()
        STAKE_OPERATIONS.labels(operation="claim").inc()

        return TransactionResponse(
            success=result.status,
            tx_hash=result.tx_hash,
            block_number=result.block_number,
            gas_used=result.gas_used,
            events=result.events
        )
    except Exception as e:
        API_ERRORS.labels(endpoint="claim").inc()
        logger.error(f"Claim error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve", response_model=TransactionResponse)
async def approve_tokens(request: ApproveRequest):
    """Approve staking contract to spend tokens."""
    if not blockchain_service or not blockchain_service.staking_contract:
        API_ERRORS.labels(endpoint="approve").inc()
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        result = blockchain_service.approve_staking(request.amount)
        STAKE_OPERATIONS.labels(operation="approve").inc()

        return TransactionResponse(
            success=result.status,
            tx_hash=result.tx_hash,
            block_number=result.block_number,
            gas_used=result.gas_used,
            events=[]
        )
    except Exception as e:
        API_ERRORS.labels(endpoint="approve").inc()
        logger.error(f"Approve error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Query Endpoints ====================

@app.get("/position/{address}", response_model=StakeInfoResponse)
async def get_position(address: str):
    """Get staking position for an address."""
    if not blockchain_service or not blockchain_service.staking_contract:
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        info = blockchain_service.get_stake_info(address)
        return StakeInfoResponse(
            address=address,
            balance=info.balance,
            pending_rewards=info.pending_rewards,
            reward_debt=info.reward_debt,
            last_updated=info.last_updated
        )
    except Exception as e:
        logger.error(f"Get position error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=ProtocolStatsResponse)
async def get_protocol_stats():
    """Get protocol-wide statistics."""
    if not blockchain_service or not blockchain_service.staking_contract:
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        total_staked = blockchain_service.get_total_staked()
        reward_rate = blockchain_service.get_reward_rate()

        # Get indexed stats if available
        indexed_stats = {}
        if event_indexer:
            indexed_stats = event_indexer.get_protocol_stats()

        return ProtocolStatsResponse(
            total_staked=total_staked,
            reward_rate=reward_rate,
            total_users=indexed_stats.get('total_users', 0),
            total_rewards_distributed=indexed_stats.get('total_rewards_distributed', 0),
            block_number=blockchain_service.block_number
        )
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events")
async def get_events(
    from_block: int = 0,
    event_type: Optional[str] = None
):
    """Get staking events from the contract."""
    if not blockchain_service or not blockchain_service.staking_contract:
        raise HTTPException(status_code=503, detail="Blockchain service not configured")

    try:
        events = blockchain_service.get_staking_events(
            from_block=from_block,
            event_type=event_type
        )
        return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Get events error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_events(background_tasks: BackgroundTasks):
    """Trigger event indexing (background task)."""
    if not event_indexer:
        raise HTTPException(status_code=503, detail="Event indexer not configured")

    background_tasks.add_task(event_indexer.index_events)
    return {"message": "Indexing started in background"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Portfolio Staking Platform API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "stake": "/stake",
            "withdraw": "/withdraw",
            "claim": "/claim",
            "approve": "/approve",
            "position": "/position/{address}",
            "stats": "/stats",
            "events": "/events"
        }
    }


def main():
    """Main entry point for the application."""
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
