"""Blockchain Oracle Service - Data aggregation and signing for on-chain delivery."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import aiohttp

LOGGER = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics the oracle can provide."""
    PORTFOLIO_VALUE = "portfolio_value"
    TOTAL_TVL = "total_tvl"
    APY = "apy"
    HEALTH_SCORE = "health_score"
    GAS_PRICE = "gas_price"
    CUSTOM = "custom"


@dataclass
class OracleRequest:
    """Represents an incoming oracle request."""
    request_id: str
    metric_type: MetricType
    parameters: Dict[str, Any] = field(default_factory=dict)
    callback_address: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class OracleResponse:
    """Represents an oracle response with signature."""
    request_id: str
    value: int
    timestamp: int
    signature: str
    signer: str
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSourceResult:
    """Result from a data source query."""
    source: str
    value: float
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataSource(ABC):
    """Abstract base class for data sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def fetch(self, metric_type: MetricType, params: Dict) -> DataSourceResult:
        pass


class PrometheusDataSource(DataSource):
    """Fetch metrics from Prometheus."""

    def __init__(self, url: str = "http://prometheus:9090"):
        self.url = url

    @property
    def name(self) -> str:
        return "prometheus"

    async def fetch(self, metric_type: MetricType, params: Dict) -> DataSourceResult:
        query_map = {
            MetricType.PORTFOLIO_VALUE: 'sum(portfolio_total_value)',
            MetricType.TOTAL_TVL: 'sum(defi_tvl_usd)',
            MetricType.APY: 'avg(protocol_apy)',
            MetricType.HEALTH_SCORE: 'min(system_health_score)',
        }

        query = params.get("query") or query_map.get(metric_type, "up")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.url}/api/v1/query",
                params={"query": query}
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Prometheus query failed: {resp.status}")

                data = await resp.json()
                results = data.get("data", {}).get("result", [])

                if not results:
                    raise Exception("No data returned from Prometheus")

                value = float(results[0]["value"][1])

                return DataSourceResult(
                    source=self.name,
                    value=value,
                    timestamp=datetime.utcnow(),
                    confidence=1.0,
                )


class APIDataSource(DataSource):
    """Fetch metrics from external API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "external_api"

    async def fetch(self, metric_type: MetricType, params: Dict) -> DataSourceResult:
        endpoint = params.get("endpoint", "/metrics")
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"API request failed: {resp.status}")

                data = await resp.json()
                value = data.get("value", data.get("result", 0))

                return DataSourceResult(
                    source=self.name,
                    value=float(value),
                    timestamp=datetime.utcnow(),
                    confidence=0.9,
                    metadata=data,
                )


class DataAggregator:
    """Aggregates data from multiple sources with outlier detection."""

    def __init__(self, sources: List[DataSource], min_sources: int = 1):
        self.sources = sources
        self.min_sources = min_sources

    async def aggregate(
        self,
        metric_type: MetricType,
        params: Dict,
        strategy: str = "median",
    ) -> Tuple[float, float, List[DataSourceResult]]:
        """
        Aggregate data from multiple sources.

        Returns:
            Tuple of (aggregated_value, confidence, individual_results)
        """
        results = []

        # Fetch from all sources concurrently
        tasks = [source.fetch(metric_type, params) for source in self.sources]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                LOGGER.warning(f"Data source failed: {response}")
                continue
            results.append(response)

        if len(results) < self.min_sources:
            raise Exception(f"Insufficient data sources: {len(results)} < {self.min_sources}")

        values = [r.value for r in results]

        # Apply aggregation strategy
        if strategy == "median":
            import statistics
            aggregated = statistics.median(values)
        elif strategy == "mean":
            aggregated = sum(values) / len(values)
        elif strategy == "min":
            aggregated = min(values)
        elif strategy == "max":
            aggregated = max(values)
        else:
            aggregated = values[0]

        # Calculate confidence based on agreement
        if len(values) > 1:
            variance = sum((v - aggregated) ** 2 for v in values) / len(values)
            confidence = max(0.5, 1.0 - (variance / (aggregated ** 2 + 1)))
        else:
            confidence = results[0].confidence

        return aggregated, confidence, results


class OracleSigner:
    """Handles ECDSA signing of oracle responses."""

    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key or os.environ.get("ORACLE_PRIVATE_KEY")
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
        else:
            # Generate a new key for testing
            self.account = Account.create()
            self.address = self.account.address
            LOGGER.warning("No private key provided, using generated key for testing")

    def sign_response(
        self,
        request_id: str,
        value: int,
        timestamp: int,
    ) -> str:
        """Sign oracle response data."""
        # Create message hash (matches Solidity keccak256)
        message_hash = Web3.solidity_keccak(
            ["bytes32", "uint256", "uint256"],
            [bytes.fromhex(request_id.replace("0x", "")), value, timestamp]
        )

        # Sign the hash
        signable = encode_defunct(message_hash)
        signed = self.account.sign_message(signable)

        return signed.signature.hex()

    def verify_signature(
        self,
        request_id: str,
        value: int,
        timestamp: int,
        signature: str,
    ) -> bool:
        """Verify a signature."""
        message_hash = Web3.solidity_keccak(
            ["bytes32", "uint256", "uint256"],
            [bytes.fromhex(request_id.replace("0x", "")), value, timestamp]
        )

        signable = encode_defunct(message_hash)
        recovered = Account.recover_message(signable, signature=bytes.fromhex(signature))

        return recovered.lower() == self.address.lower()


class RequestQueue:
    """Queue for managing oracle requests with retry logic."""

    def __init__(self, max_size: int = 1000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.processing: Dict[str, OracleRequest] = {}
        self.completed: Dict[str, OracleResponse] = {}
        self._lock = asyncio.Lock()

    async def enqueue(self, request: OracleRequest) -> None:
        """Add a request to the queue."""
        await self.queue.put(request)
        LOGGER.info(f"Enqueued request: {request.request_id}")

    async def dequeue(self) -> Optional[OracleRequest]:
        """Get the next request from the queue."""
        try:
            request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            async with self._lock:
                self.processing[request.request_id] = request
            return request
        except asyncio.TimeoutError:
            return None

    async def complete(self, request_id: str, response: OracleResponse) -> None:
        """Mark a request as completed."""
        async with self._lock:
            if request_id in self.processing:
                del self.processing[request_id]
            self.completed[request_id] = response

    async def retry(self, request: OracleRequest) -> bool:
        """Retry a failed request."""
        if request.retry_count >= request.max_retries:
            LOGGER.error(f"Request {request.request_id} exceeded max retries")
            return False

        request.retry_count += 1
        await self.enqueue(request)
        return True

    def get_status(self, request_id: str) -> Optional[Dict]:
        """Get the status of a request."""
        if request_id in self.completed:
            return {"status": "completed", "response": self.completed[request_id]}
        if request_id in self.processing:
            return {"status": "processing"}
        return {"status": "pending"}


class OracleService:
    """Main oracle service orchestrating data fetching, aggregation, and signing."""

    def __init__(
        self,
        aggregator: DataAggregator,
        signer: OracleSigner,
        queue: Optional[RequestQueue] = None,
    ):
        self.aggregator = aggregator
        self.signer = signer
        self.queue = queue or RequestQueue()
        self._running = False
        self._cache: Dict[str, Tuple[OracleResponse, datetime]] = {}
        self._cache_ttl = timedelta(seconds=60)

    async def process_request(self, request: OracleRequest) -> OracleResponse:
        """Process a single oracle request."""
        cache_key = f"{request.metric_type.value}:{json.dumps(request.parameters, sort_keys=True)}"

        # Check cache
        if cache_key in self._cache:
            cached_response, cached_time = self._cache[cache_key]
            if datetime.utcnow() - cached_time < self._cache_ttl:
                LOGGER.info(f"Returning cached response for {request.request_id}")
                return OracleResponse(
                    request_id=request.request_id,
                    value=cached_response.value,
                    timestamp=cached_response.timestamp,
                    signature=self.signer.sign_response(
                        request.request_id,
                        cached_response.value,
                        cached_response.timestamp,
                    ),
                    signer=self.signer.address,
                    raw_data=cached_response.raw_data,
                )

        # Aggregate data
        value, confidence, results = await self.aggregator.aggregate(
            request.metric_type,
            request.parameters,
        )

        # Scale to integer (18 decimals like ERC20)
        scaled_value = int(value * 10**18)
        timestamp = int(time.time())

        # Sign the response
        signature = self.signer.sign_response(
            request.request_id,
            scaled_value,
            timestamp,
        )

        response = OracleResponse(
            request_id=request.request_id,
            value=scaled_value,
            timestamp=timestamp,
            signature=signature,
            signer=self.signer.address,
            raw_data={
                "raw_value": value,
                "confidence": confidence,
                "sources": [r.source for r in results],
            },
        )

        # Update cache
        self._cache[cache_key] = (response, datetime.utcnow())

        return response

    async def start_worker(self) -> None:
        """Start the request processing worker."""
        self._running = True
        LOGGER.info("Oracle worker started")

        while self._running:
            request = await self.queue.dequeue()
            if request is None:
                continue

            try:
                response = await self.process_request(request)
                await self.queue.complete(request.request_id, response)
                LOGGER.info(f"Processed request: {request.request_id}")

            except Exception as e:
                LOGGER.error(f"Failed to process request {request.request_id}: {e}")
                if not await self.queue.retry(request):
                    LOGGER.error(f"Request {request.request_id} permanently failed")

    def stop_worker(self) -> None:
        """Stop the worker."""
        self._running = False


def create_oracle_service() -> OracleService:
    """Factory function to create an oracle service with default configuration."""
    sources = [
        PrometheusDataSource(os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")),
    ]

    api_url = os.environ.get("EXTERNAL_API_URL")
    if api_url:
        sources.append(APIDataSource(api_url, os.environ.get("EXTERNAL_API_KEY")))

    aggregator = DataAggregator(sources, min_sources=1)
    signer = OracleSigner()

    return OracleService(aggregator, signer)
