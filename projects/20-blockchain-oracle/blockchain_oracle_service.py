"""Advanced blockchain oracle service implementation.

This module defines a complete oracle platform that aggregates off-chain
signals, computes resilient price feeds, and publishes them on-chain with
cryptographic guarantees.  The architecture mirrors production-grade oracle
networks with layered redundancy, signature management, queuing, and
observability hooks.

The code focuses on structure, orchestration, and patterns that engineers can
adapt when integrating with real exchanges and blockchains.  External calls are
mocked/simulated to keep the module self-contained while demonstrating the
interfaces that would wrap providers such as Chainlink, Pyth, or custom
smart-contracts.
"""

from __future__ import annotations

import asyncio
import contextlib
import hmac
import json
import logging
import random
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
from typing import Any, Awaitable, Callable, Deque, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger("blockchain_oracle")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Configuration data classes
# ---------------------------------------------------------------------------

@dataclass
class FeedConfig:
    """Configuration for an individual data feed."""

    name: str
    weight: Decimal = Decimal("1")
    tolerance_bps: int = 100  # allowed drift from aggregate in basis points
    jitter_seconds: Tuple[float, float] = (0.1, 0.5)


@dataclass
class OracleConfig:
    """Top-level configuration for the oracle service."""

    publish_interval: float = 10.0
    quorum: int = 3
    signing_key: bytes = b"demo-signing-key"
    max_queue: int = 512
    alert_callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None
    staleness_threshold: float = 30.0  # seconds


@dataclass
class OracleDataPoint:
    """Normalized data point returned from a feed."""

    feed: str
    value: Decimal
    timestamp: float = field(default_factory=lambda: time.time())
    raw: Dict[str, Any] = field(default_factory=dict)

    def serialize(self) -> Dict[str, Any]:
        return {
            "feed": self.feed,
            "value": str(self.value),
            "timestamp": self.timestamp,
            "raw": self.raw,
        }


# ---------------------------------------------------------------------------
# Feed implementations
# ---------------------------------------------------------------------------

class BaseDataFeed:
    """Base class for oracle data feeds.

    Concrete feeds override :meth:`fetch` to supply market data.  The default
    implementation simulates exchange data to keep the module runnable without
    credentials.
    """

    def __init__(self, config: FeedConfig):
        self.config = config
        self._last_value: Optional[Decimal] = None

    async def fetch(self) -> OracleDataPoint:
        raise NotImplementedError

    async def _simulate_latency(self) -> None:
        low, high = self.config.jitter_seconds
        await asyncio.sleep(random.uniform(low, high))

    def _set_last_value(self, value: Decimal) -> None:
        self._last_value = value

    def _fallback_value(self) -> Decimal:
        if self._last_value is None:
            # Provide deterministic fallback to keep demos stable.
            self._last_value = Decimal("1000") + Decimal(random.randint(-5, 5))
        return self._last_value


class SimulatedExchangeFeed(BaseDataFeed):
    """Generates pseudo-random prices following a gentle random walk."""

    def __init__(self, config: FeedConfig, drift: Decimal = Decimal("0")):
        super().__init__(config)
        self.drift = drift

    async def fetch(self) -> OracleDataPoint:
        await self._simulate_latency()
        base = self._fallback_value()
        delta = Decimal(random.uniform(-1, 1)) + self.drift
        value = base + delta
        self._set_last_value(value)
        return OracleDataPoint(feed=self.config.name, value=value)


class DeterministicFeed(BaseDataFeed):
    """Feed returning deterministic values useful for integration tests."""

    def __init__(self, config: FeedConfig, sequence: Iterable[Decimal]):
        super().__init__(config)
        self._sequence = iter(sequence)

    async def fetch(self) -> OracleDataPoint:
        await self._simulate_latency()
        try:
            value = next(self._sequence)
        except StopIteration:
            value = self._fallback_value()
        self._set_last_value(value)
        return OracleDataPoint(feed=self.config.name, value=value)


# ---------------------------------------------------------------------------
# Circuit breaker & anomaly detection
# ---------------------------------------------------------------------------

class CircuitBreaker:
    """Protects the oracle from noisy or failing feeds."""

    def __init__(self, name: str, failure_threshold: int = 3, cooldown: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self._failure_count = 0
        self._tripped_until: float = 0.0

    def record_success(self) -> None:
        self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._tripped_until = time.time() + self.cooldown
            logger.warning("Circuit breaker tripped for feed %s", self.name)

    def is_open(self) -> bool:
        if time.time() < self._tripped_until:
            return True
        if self._tripped_until:
            # Reset when cooldown expires.
            self._tripped_until = 0.0
            self._failure_count = 0
        return False


class AnomalyDetector:
    """Detects outliers compared to the aggregate median."""

    def __init__(self, tolerance_bps: int):
        self.tolerance_bps = tolerance_bps

    def is_anomalous(self, value: Decimal, reference: Decimal) -> bool:
        if reference == 0:
            return False
        delta = abs(value - reference)
        basis_points = (delta / reference) * Decimal("10000")
        return basis_points > Decimal(self.tolerance_bps)


# ---------------------------------------------------------------------------
# Aggregation & signing
# ---------------------------------------------------------------------------

class OracleAggregator:
    """Aggregates data points from feeds and produces signed payloads."""

    def __init__(self, config: OracleConfig, feeds: Dict[str, BaseDataFeed]):
        self.config = config
        self.feeds = feeds
        self.circuit_breakers = {
            name: CircuitBreaker(name) for name in feeds
        }
        self.history: Deque[Dict[str, Any]] = deque(maxlen=128)

    async def collect(self) -> List[OracleDataPoint]:
        """Fetch data from all feeds concurrently with circuit breaker checks."""

        async def _fetch(name: str, feed: BaseDataFeed) -> Optional[OracleDataPoint]:
            breaker = self.circuit_breakers[name]
            if breaker.is_open():
                logger.debug("Skipping feed %s due to open circuit", name)
                return None
            try:
                result = await feed.fetch()
                breaker.record_success()
                return result
            except Exception as exc:  # pragma: no cover - defensive logging
                breaker.record_failure()
                logger.exception("Feed %s failed: %s", name, exc)
                return None

        tasks = [asyncio.create_task(_fetch(name, feed)) for name, feed in self.feeds.items()]
        results = await asyncio.gather(*tasks)
        return [res for res in results if res is not None]

    def _weighted_median(self, datapoints: List[OracleDataPoint]) -> Decimal:
        """Compute a weighted median of feed values."""
        weighted_values: List[Tuple[Decimal, Decimal]] = []
        for data in datapoints:
            weight = self.feeds[data.feed].config.weight
            weighted_values.append((data.value, weight))

        weighted_values.sort(key=lambda item: item[0])
        total_weight = sum(weight for _, weight in weighted_values)
        threshold = total_weight / Decimal("2")
        cumulative = Decimal("0")

        for value, weight in weighted_values:
            cumulative += weight
            if cumulative >= threshold:
                return value
        # Fallback to arithmetic mean if weights misconfigured
        return statistics.mean(value for value, _ in weighted_values)

    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        message = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(self.config.signing_key, message, sha256).hexdigest()
        return signature

    async def aggregate(self) -> Optional[Dict[str, Any]]:
        datapoints = await self.collect()
        if len(datapoints) < self.config.quorum:
            logger.warning(
                "Quorum not met (have %s, need %s)", len(datapoints), self.config.quorum
            )
            return None

        median = self._weighted_median(datapoints)

        filtered: List[OracleDataPoint] = []
        for data in datapoints:
            detector = AnomalyDetector(self.feeds[data.feed].config.tolerance_bps)
            if detector.is_anomalous(data.value, median):
                logger.info("Feed %s flagged as anomaly (value=%s, median=%s)", data.feed, data.value, median)
                continue
            filtered.append(data)

        if len(filtered) < self.config.quorum:
            logger.warning("Quorum lost after anomaly filtering; aborting publish")
            return None

        payload = {
            "timestamp": time.time(),
            "median": str(self._weighted_median(filtered)),
            "data": [point.serialize() for point in filtered],
        }
        payload["signature"] = self._sign_payload(payload)
        self.history.append(payload)
        return payload


# ---------------------------------------------------------------------------
# Blockchain publishing & durability
# ---------------------------------------------------------------------------

class BlockchainPublisher:
    """Publishes payloads to on-chain targets with durable queuing."""

    def __init__(self, config: OracleConfig):
        self.config = config
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=config.max_queue)
        self.pending: Deque[Dict[str, Any]] = deque()

    async def publish(self, payload: Dict[str, Any]) -> None:
        """Simulate an on-chain transaction submission.

        Real implementations would integrate with `web3.py`, `ethers`, or
        similar libraries.  Here we emulate network latency, sporadic failures,
        and durable queuing for failed attempts.
        """

        await asyncio.sleep(random.uniform(0.1, 0.3))
        if random.random() < 0.1:
            raise RuntimeError("Simulated transaction failure")
        logger.info("Published payload at median=%s", payload["median"])

    async def submit(self, payload: Dict[str, Any]) -> None:
        try:
            await self.publish(payload)
        except Exception as exc:
            logger.error("Publish failed, queueing payload: %s", exc)
            with contextlib.suppress(asyncio.QueueFull):
                await self.queue.put(payload)

    async def flush_queue(self) -> None:
        while not self.queue.empty():
            payload = await self.queue.get()
            try:
                await self.publish(payload)
            except Exception as exc:
                logger.error("Retry failed: %s", exc)
                await asyncio.sleep(1)
                with contextlib.suppress(asyncio.QueueFull):
                    await self.queue.put(payload)
                break


# ---------------------------------------------------------------------------
# Proof-of-reserve monitoring
# ---------------------------------------------------------------------------

@dataclass
class ReserveSnapshot:
    total_assets: Decimal
    total_liabilities: Decimal
    timestamp: float = field(default_factory=lambda: time.time())

    @property
    def collateralization_ratio(self) -> Decimal:
        if self.total_liabilities == 0:
            return Decimal("1")
        return self.total_assets / self.total_liabilities


class ProofOfReserveMonitor:
    """Tracks reserve attestations for transparency."""

    def __init__(self, fetcher: Callable[[], Awaitable[ReserveSnapshot]]):
        self.fetcher = fetcher
        self.history: Deque[ReserveSnapshot] = deque(maxlen=96)

    async def sample(self) -> ReserveSnapshot:
        snapshot = await self.fetcher()
        self.history.append(snapshot)
        logger.debug(
            "Proof-of-reserve snapshot: assets=%s liabilities=%s ratio=%.4f",
            snapshot.total_assets,
            snapshot.total_liabilities,
            float(snapshot.collateralization_ratio),
        )
        return snapshot


# ---------------------------------------------------------------------------
# Oracle service orchestration
# ---------------------------------------------------------------------------

class OracleService:
    """High-level orchestrator combining aggregation, publishing, and monitoring."""

    def __init__(
        self,
        config: OracleConfig,
        feeds: Dict[str, BaseDataFeed],
        reserve_monitor: ProofOfReserveMonitor,
    ):
        self.config = config
        self.aggregator = OracleAggregator(config, feeds)
        self.publisher = BlockchainPublisher(config)
        self.reserve_monitor = reserve_monitor
        self._stop_event = asyncio.Event()

    async def _publish_loop(self) -> None:
        while not self._stop_event.is_set():
            start = time.time()
            payload = await self.aggregator.aggregate()
            if payload:
                await self.publisher.submit(payload)
            await self.publisher.flush_queue()
            elapsed = time.time() - start
            wait_time = max(0.0, self.config.publish_interval - elapsed)
            await asyncio.wait({asyncio.create_task(self._stop_event.wait())}, timeout=wait_time)

    async def _reserve_loop(self) -> None:
        while not self._stop_event.is_set():
            snapshot = await self.reserve_monitor.sample()
            if snapshot.collateralization_ratio < Decimal("1"):
                await self._emit_alert(
                    "reserve_under_collateralized",
                    {
                        "ratio": float(snapshot.collateralization_ratio),
                        "timestamp": snapshot.timestamp,
                    },
                )
            await asyncio.wait({asyncio.create_task(self._stop_event.wait())}, timeout=60.0)

    async def _emit_alert(self, name: str, payload: Dict[str, Any]) -> None:
        if self.config.alert_callback:
            await self.config.alert_callback(name, payload)
        else:
            logger.warning("ALERT %s: %s", name, payload)

    async def start(self) -> None:
        logger.info("Starting oracle service with %s feeds", len(self.aggregator.feeds))
        publish_task = asyncio.create_task(self._publish_loop())
        reserve_task = asyncio.create_task(self._reserve_loop())
        try:
            await asyncio.wait({publish_task, reserve_task}, return_when=asyncio.FIRST_COMPLETED)
        finally:
            self._stop_event.set()
            publish_task.cancel()
            reserve_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await publish_task
                await reserve_task

    def stop(self) -> None:
        self._stop_event.set()


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------

async def simulated_reserve_fetcher() -> ReserveSnapshot:
    await asyncio.sleep(0.2)
    assets = Decimal("1000000") + Decimal(random.randint(-5000, 5000))
    liabilities = Decimal("900000") + Decimal(random.randint(-3000, 3000))
    return ReserveSnapshot(total_assets=assets, total_liabilities=liabilities)


def build_demo_service() -> OracleService:
    feeds: Dict[str, BaseDataFeed] = {
        "alpha": SimulatedExchangeFeed(FeedConfig(name="alpha", weight=Decimal("1.2"))),
        "beta": SimulatedExchangeFeed(FeedConfig(name="beta", weight=Decimal("0.8"), tolerance_bps=150)),
        "gamma": SimulatedExchangeFeed(FeedConfig(name="gamma", weight=Decimal("1.0"), jitter_seconds=(0.05, 0.1))),
    }
    config = OracleConfig(publish_interval=5.0, quorum=2)
    reserve_monitor = ProofOfReserveMonitor(simulated_reserve_fetcher)
    return OracleService(config=config, feeds=feeds, reserve_monitor=reserve_monitor)


async def run_demo(duration: float = 20.0) -> None:
    service = build_demo_service()
    runner = asyncio.create_task(service.start())
    await asyncio.sleep(duration)
    service.stop()
    with contextlib.suppress(asyncio.CancelledError):
        await runner


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        pass
