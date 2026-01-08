"""Distributed GPU computing using Dask for large-scale simulations."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import numpy as np

try:
    import dask
    import dask.array as da
    from dask.distributed import Client, LocalCluster, get_client
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    da = None
    Client = None

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    cp = np
    GPU_AVAILABLE = False

LOGGER = logging.getLogger(__name__)


@dataclass
class ClusterConfig:
    """Configuration for distributed cluster."""
    n_workers: int = 4
    threads_per_worker: int = 2
    memory_limit: str = "4GB"
    scheduler_address: Optional[str] = None  # For connecting to existing cluster
    use_gpu: bool = True


@dataclass
class DistributedResult:
    """Result from distributed computation."""
    result: Any
    execution_time_ms: float
    n_workers: int
    n_tasks: int
    memory_used_mb: float


class DistributedSimulator:
    """Distributed GPU computing for large-scale financial simulations."""

    def __init__(self, config: Optional[ClusterConfig] = None):
        if not DASK_AVAILABLE:
            raise RuntimeError("Dask not installed - distributed computing unavailable")

        self.config = config or ClusterConfig()
        self._client: Optional[Client] = None
        self._cluster = None

    def start_cluster(self) -> None:
        """Start or connect to a Dask cluster."""
        if self.config.scheduler_address:
            LOGGER.info(f"Connecting to existing cluster: {self.config.scheduler_address}")
            self._client = Client(self.config.scheduler_address)
        else:
            LOGGER.info(f"Starting local cluster with {self.config.n_workers} workers")
            self._cluster = LocalCluster(
                n_workers=self.config.n_workers,
                threads_per_worker=self.config.threads_per_worker,
                memory_limit=self.config.memory_limit,
            )
            self._client = Client(self._cluster)

        LOGGER.info(f"Dashboard: {self._client.dashboard_link}")

    def stop_cluster(self) -> None:
        """Stop the Dask cluster."""
        if self._client:
            self._client.close()
        if self._cluster:
            self._cluster.close()

    @property
    def client(self) -> Client:
        """Get the Dask client, starting cluster if needed."""
        if self._client is None:
            self.start_cluster()
        return self._client

    def monte_carlo_distributed(
        self,
        n_simulations: int,
        n_steps: int,
        simulation_func: Callable,
        chunk_size: int = 100000,
        **kwargs,
    ) -> DistributedResult:
        """
        Run Monte Carlo simulations distributed across workers.

        Args:
            n_simulations: Total number of simulations
            n_steps: Number of steps per simulation
            simulation_func: Function to run on each chunk
            chunk_size: Size of each chunk to distribute
            **kwargs: Additional arguments for simulation_func

        Returns:
            DistributedResult with aggregated results
        """
        start_time = time.time()

        # Create chunks
        n_chunks = (n_simulations + chunk_size - 1) // chunk_size
        chunks = []

        for i in range(n_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, n_simulations)
            chunk_sims = end_idx - start_idx
            chunks.append(chunk_sims)

        LOGGER.info(f"Distributing {n_simulations} simulations across {n_chunks} chunks")

        # Submit tasks to workers
        futures = []
        for chunk_sims in chunks:
            future = self.client.submit(
                simulation_func,
                n_simulations=chunk_sims,
                n_steps=n_steps,
                use_gpu=self.config.use_gpu and GPU_AVAILABLE,
                **kwargs,
            )
            futures.append(future)

        # Gather results
        results = self.client.gather(futures)

        # Aggregate results
        aggregated = self._aggregate_results(results)

        execution_time = (time.time() - start_time) * 1000

        return DistributedResult(
            result=aggregated,
            execution_time_ms=execution_time,
            n_workers=len(self.client.scheduler_info()["workers"]),
            n_tasks=n_chunks,
            memory_used_mb=self._get_memory_usage(),
        )

    def _aggregate_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Aggregate results from multiple workers."""
        if not results:
            return {}

        # Combine arrays
        all_returns = np.concatenate([r.get("returns", []) for r in results])
        all_final_values = np.concatenate([r.get("final_values", []) for r in results])

        # Recalculate aggregate statistics
        return {
            "returns": all_returns,
            "final_values": all_final_values,
            "mean_return": float(np.mean(all_returns)),
            "volatility": float(np.std(all_returns)),
            "var_95": float(np.percentile(all_returns, 5)),
            "var_99": float(np.percentile(all_returns, 1)),
            "n_simulations": len(all_returns),
        }

    def _get_memory_usage(self) -> float:
        """Get total memory usage across workers."""
        try:
            info = self.client.scheduler_info()
            total_memory = sum(
                w.get("memory", 0) for w in info.get("workers", {}).values()
            )
            return total_memory / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0

    def map_reduce(
        self,
        data: np.ndarray,
        map_func: Callable,
        reduce_func: Callable,
        chunk_size: int = 10000,
    ) -> DistributedResult:
        """
        Perform map-reduce operation on data.

        Args:
            data: Input data array
            map_func: Function to apply to each chunk
            reduce_func: Function to reduce results
            chunk_size: Size of each chunk
        """
        start_time = time.time()

        # Create Dask array
        dask_data = da.from_array(data, chunks=chunk_size)

        # Apply map function
        mapped = dask_data.map_blocks(map_func, dtype=data.dtype)

        # Reduce
        result = reduce_func(mapped).compute()

        execution_time = (time.time() - start_time) * 1000

        return DistributedResult(
            result=result,
            execution_time_ms=execution_time,
            n_workers=len(self.client.scheduler_info()["workers"]),
            n_tasks=len(dask_data.chunks[0]),
            memory_used_mb=self._get_memory_usage(),
        )

    def parallel_option_pricing(
        self,
        spots: np.ndarray,
        strikes: np.ndarray,
        rates: np.ndarray,
        volatilities: np.ndarray,
        times: np.ndarray,
        chunk_size: int = 50000,
    ) -> DistributedResult:
        """
        Price options in parallel across workers.
        """
        start_time = time.time()

        n_options = len(spots)
        n_chunks = (n_options + chunk_size - 1) // chunk_size

        futures = []
        for i in range(n_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, n_options)

            future = self.client.submit(
                _price_options_chunk,
                spots[start_idx:end_idx],
                strikes[start_idx:end_idx],
                rates[start_idx:end_idx],
                volatilities[start_idx:end_idx],
                times[start_idx:end_idx],
                use_gpu=self.config.use_gpu and GPU_AVAILABLE,
            )
            futures.append(future)

        results = self.client.gather(futures)

        # Combine results
        prices = np.concatenate([r["prices"] for r in results])
        deltas = np.concatenate([r["deltas"] for r in results])

        execution_time = (time.time() - start_time) * 1000

        return DistributedResult(
            result={"prices": prices, "deltas": deltas},
            execution_time_ms=execution_time,
            n_workers=len(self.client.scheduler_info()["workers"]),
            n_tasks=n_chunks,
            memory_used_mb=self._get_memory_usage(),
        )


def _price_options_chunk(
    spots: np.ndarray,
    strikes: np.ndarray,
    rates: np.ndarray,
    volatilities: np.ndarray,
    times: np.ndarray,
    use_gpu: bool = False,
) -> Dict[str, np.ndarray]:
    """Worker function to price a chunk of options."""
    from scipy.stats import norm

    xp = cp if use_gpu and GPU_AVAILABLE else np

    if use_gpu and GPU_AVAILABLE:
        spots = cp.asarray(spots)
        strikes = cp.asarray(strikes)
        rates = cp.asarray(rates)
        volatilities = cp.asarray(volatilities)
        times = cp.asarray(times)

    sqrt_t = xp.sqrt(times)
    d1 = (xp.log(spots / strikes) + (rates + 0.5 * volatilities**2) * times) / (volatilities * sqrt_t)
    d2 = d1 - volatilities * sqrt_t

    if use_gpu and GPU_AVAILABLE:
        # GPU-based normal CDF approximation
        cdf_d1 = 0.5 * (1 + xp.erf(d1 / xp.sqrt(2)))
        cdf_d2 = 0.5 * (1 + xp.erf(d2 / xp.sqrt(2)))
    else:
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)

    prices = spots * cdf_d1 - strikes * xp.exp(-rates * times) * cdf_d2
    deltas = cdf_d1

    if use_gpu and GPU_AVAILABLE:
        prices = cp.asnumpy(prices)
        deltas = cp.asnumpy(deltas)

    return {"prices": prices.astype(np.float32), "deltas": deltas.astype(np.float32)}


def run_simulation_chunk(
    n_simulations: int,
    n_steps: int,
    use_gpu: bool = False,
    S0: float = 100.0,
    mu: float = 0.08,
    sigma: float = 0.2,
    T: float = 1.0,
) -> Dict[str, np.ndarray]:
    """Worker function to run simulation chunk."""
    xp = cp if use_gpu and GPU_AVAILABLE else np

    dt = T / n_steps
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * xp.sqrt(dt)

    random_normals = xp.random.standard_normal((n_simulations, n_steps))
    log_returns = drift + diffusion * random_normals
    cumulative = xp.cumsum(log_returns, axis=1)
    final_log_returns = cumulative[:, -1]

    final_values = S0 * xp.exp(final_log_returns)
    returns = (final_values - S0) / S0

    if use_gpu and GPU_AVAILABLE:
        returns = cp.asnumpy(returns)
        final_values = cp.asnumpy(final_values)

    return {
        "returns": returns.astype(np.float32),
        "final_values": final_values.astype(np.float32),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if not DASK_AVAILABLE:
        print("Dask not available. Install with: pip install dask[distributed]")
        exit(1)

    config = ClusterConfig(n_workers=4, use_gpu=GPU_AVAILABLE)
    simulator = DistributedSimulator(config)

    try:
        simulator.start_cluster()

        # Run distributed Monte Carlo
        result = simulator.monte_carlo_distributed(
            n_simulations=1000000,
            n_steps=252,
            simulation_func=run_simulation_chunk,
            chunk_size=100000,
        )

        print(f"\nDistributed Simulation Results:")
        print(f"  Mean Return: {result.result['mean_return']:.2%}")
        print(f"  Volatility: {result.result['volatility']:.2%}")
        print(f"  VaR 95%: {result.result['var_95']:.2%}")
        print(f"  VaR 99%: {result.result['var_99']:.2%}")
        print(f"\nExecution Stats:")
        print(f"  Time: {result.execution_time_ms:.2f}ms")
        print(f"  Workers: {result.n_workers}")
        print(f"  Tasks: {result.n_tasks}")

    finally:
        simulator.stop_cluster()
