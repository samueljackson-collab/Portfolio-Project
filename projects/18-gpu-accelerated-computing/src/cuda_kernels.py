"""Custom CUDA kernels for GPU-accelerated financial computations."""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np

try:
    import cupy as cp
    from cupy import RawKernel
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    cp = None
    RawKernel = None

LOGGER = logging.getLogger(__name__)


# Custom CUDA kernel for option pricing (Black-Scholes)
BLACK_SCHOLES_KERNEL = """
extern "C" __global__
void black_scholes_call(
    const float* spot,
    const float* strike,
    const float* rate,
    const float* volatility,
    const float* time_to_expiry,
    float* call_price,
    float* delta,
    int n
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= n) return;

    float S = spot[idx];
    float K = strike[idx];
    float r = rate[idx];
    float sigma = volatility[idx];
    float T = time_to_expiry[idx];

    // Calculate d1 and d2
    float sqrt_T = sqrtf(T);
    float d1 = (logf(S / K) + (r + 0.5f * sigma * sigma) * T) / (sigma * sqrt_T);
    float d2 = d1 - sigma * sqrt_T;

    // Normal CDF approximation (Abramowitz and Stegun)
    float cdf_d1, cdf_d2;

    // CDF for d1
    float t1 = 1.0f / (1.0f + 0.2316419f * fabsf(d1));
    float poly1 = t1 * (0.319381530f + t1 * (-0.356563782f + t1 * (1.781477937f + t1 * (-1.821255978f + t1 * 1.330274429f))));
    float pdf1 = 0.3989422804f * expf(-0.5f * d1 * d1);
    cdf_d1 = (d1 >= 0) ? (1.0f - pdf1 * poly1) : (pdf1 * poly1);

    // CDF for d2
    float t2 = 1.0f / (1.0f + 0.2316419f * fabsf(d2));
    float poly2 = t2 * (0.319381530f + t2 * (-0.356563782f + t2 * (1.781477937f + t2 * (-1.821255978f + t2 * 1.330274429f))));
    float pdf2 = 0.3989422804f * expf(-0.5f * d2 * d2);
    cdf_d2 = (d2 >= 0) ? (1.0f - pdf2 * poly2) : (pdf2 * poly2);

    // Call price
    call_price[idx] = S * cdf_d1 - K * expf(-r * T) * cdf_d2;

    // Delta
    delta[idx] = cdf_d1;
}
"""

# CUDA kernel for Monte Carlo path generation
MONTE_CARLO_PATH_KERNEL = """
extern "C" __global__
void generate_gbm_paths(
    const float* random_normals,
    float S0,
    float mu,
    float sigma,
    float dt,
    float* paths,
    int n_paths,
    int n_steps
) {
    int path_idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (path_idx >= n_paths) return;

    float S = S0;
    float drift = (mu - 0.5f * sigma * sigma) * dt;
    float diffusion = sigma * sqrtf(dt);

    for (int step = 0; step < n_steps; step++) {
        int idx = path_idx * n_steps + step;
        float dW = random_normals[idx];
        S = S * expf(drift + diffusion * dW);
        paths[idx] = S;
    }
}
"""

# CUDA kernel for VaR/CVaR calculation
VAR_KERNEL = """
extern "C" __global__
void calculate_portfolio_var(
    const float* returns,
    const float* sorted_indices,
    float* var_contribution,
    int n,
    int cutoff_idx
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= cutoff_idx) return;

    int sorted_idx = (int)sorted_indices[idx];
    var_contribution[idx] = returns[sorted_idx];
}
"""


class CUDAKernels:
    """Collection of custom CUDA kernels for financial computations."""

    def __init__(self):
        if not GPU_AVAILABLE:
            raise RuntimeError("CuPy not available - CUDA kernels cannot be used")

        self._black_scholes = RawKernel(BLACK_SCHOLES_KERNEL, "black_scholes_call")
        self._gbm_paths = RawKernel(MONTE_CARLO_PATH_KERNEL, "generate_gbm_paths")
        self._var_calc = RawKernel(VAR_KERNEL, "calculate_portfolio_var")

        LOGGER.info("CUDA kernels compiled successfully")

    def black_scholes_vectorized(
        self,
        spot: np.ndarray,
        strike: np.ndarray,
        rate: np.ndarray,
        volatility: np.ndarray,
        time_to_expiry: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Vectorized Black-Scholes call option pricing using custom CUDA kernel.

        Returns:
            Tuple of (call_prices, deltas)
        """
        n = len(spot)

        # Transfer to GPU
        spot_gpu = cp.asarray(spot, dtype=cp.float32)
        strike_gpu = cp.asarray(strike, dtype=cp.float32)
        rate_gpu = cp.asarray(rate, dtype=cp.float32)
        vol_gpu = cp.asarray(volatility, dtype=cp.float32)
        tte_gpu = cp.asarray(time_to_expiry, dtype=cp.float32)

        # Output arrays
        call_prices = cp.zeros(n, dtype=cp.float32)
        deltas = cp.zeros(n, dtype=cp.float32)

        # Launch kernel
        block_size = 256
        grid_size = (n + block_size - 1) // block_size

        self._black_scholes(
            (grid_size,), (block_size,),
            (spot_gpu, strike_gpu, rate_gpu, vol_gpu, tte_gpu, call_prices, deltas, n)
        )

        return cp.asnumpy(call_prices), cp.asnumpy(deltas)

    def generate_gbm_paths(
        self,
        S0: float,
        mu: float,
        sigma: float,
        T: float,
        n_paths: int,
        n_steps: int,
    ) -> np.ndarray:
        """
        Generate Geometric Brownian Motion paths using custom CUDA kernel.

        Args:
            S0: Initial stock price
            mu: Drift (expected return)
            sigma: Volatility
            T: Time horizon
            n_paths: Number of paths to simulate
            n_steps: Number of time steps

        Returns:
            Array of shape (n_paths, n_steps) with simulated prices
        """
        dt = T / n_steps

        # Generate random normals on GPU
        random_normals = cp.random.standard_normal((n_paths, n_steps), dtype=cp.float32)

        # Output array
        paths = cp.zeros((n_paths, n_steps), dtype=cp.float32)

        # Launch kernel
        block_size = 256
        grid_size = (n_paths + block_size - 1) // block_size

        self._gbm_paths(
            (grid_size,), (block_size,),
            (random_normals, cp.float32(S0), cp.float32(mu), cp.float32(sigma),
             cp.float32(dt), paths, n_paths, n_steps)
        )

        return cp.asnumpy(paths)


class CPUFallback:
    """CPU fallback implementations when CUDA is not available."""

    @staticmethod
    def black_scholes_vectorized(
        spot: np.ndarray,
        strike: np.ndarray,
        rate: np.ndarray,
        volatility: np.ndarray,
        time_to_expiry: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """CPU implementation of Black-Scholes."""
        from scipy.stats import norm

        sqrt_T = np.sqrt(time_to_expiry)
        d1 = (np.log(spot / strike) + (rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * sqrt_T)
        d2 = d1 - volatility * sqrt_T

        call_prices = spot * norm.cdf(d1) - strike * np.exp(-rate * time_to_expiry) * norm.cdf(d2)
        deltas = norm.cdf(d1)

        return call_prices.astype(np.float32), deltas.astype(np.float32)

    @staticmethod
    def generate_gbm_paths(
        S0: float,
        mu: float,
        sigma: float,
        T: float,
        n_paths: int,
        n_steps: int,
    ) -> np.ndarray:
        """CPU implementation of GBM path generation."""
        dt = T / n_steps
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)

        random_normals = np.random.standard_normal((n_paths, n_steps))
        log_returns = drift + diffusion * random_normals

        paths = S0 * np.exp(np.cumsum(log_returns, axis=1))
        return paths.astype(np.float32)


def get_kernels():
    """Factory function to get appropriate kernel implementation."""
    if GPU_AVAILABLE:
        try:
            return CUDAKernels()
        except Exception as e:
            LOGGER.warning(f"Failed to initialize CUDA kernels: {e}")

    LOGGER.info("Using CPU fallback implementations")
    return CPUFallback()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test Black-Scholes pricing
    n = 10000
    spot = np.random.uniform(90, 110, n).astype(np.float32)
    strike = np.full(n, 100, dtype=np.float32)
    rate = np.full(n, 0.05, dtype=np.float32)
    vol = np.full(n, 0.2, dtype=np.float32)
    tte = np.full(n, 1.0, dtype=np.float32)

    kernels = get_kernels()

    import time
    start = time.time()
    prices, deltas = kernels.black_scholes_vectorized(spot, strike, rate, vol, tte)
    elapsed = (time.time() - start) * 1000

    print(f"Priced {n} options in {elapsed:.2f}ms")
    print(f"Sample prices: {prices[:5]}")
    print(f"Sample deltas: {deltas[:5]}")

    # Test GBM path generation
    start = time.time()
    paths = kernels.generate_gbm_paths(100.0, 0.08, 0.2, 1.0, 10000, 252)
    elapsed = (time.time() - start) * 1000

    print(f"\nGenerated {paths.shape[0]} paths with {paths.shape[1]} steps in {elapsed:.2f}ms")
    print(f"Final prices range: [{paths[:, -1].min():.2f}, {paths[:, -1].max():.2f}]")
