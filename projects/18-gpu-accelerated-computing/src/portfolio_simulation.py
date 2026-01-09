"""GPU-accelerated portfolio simulation with risk metrics."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    cp = np
    GPU_AVAILABLE = False

LOGGER = logging.getLogger(__name__)


@dataclass
class Asset:
    """Represents a portfolio asset."""
    symbol: str
    weight: float
    expected_return: float  # Annual
    volatility: float  # Annual std dev


@dataclass
class PortfolioConfig:
    """Configuration for portfolio simulation."""
    assets: List[Asset]
    correlation_matrix: Optional[np.ndarray] = None
    time_horizon_days: int = 252  # 1 trading year
    risk_free_rate: float = 0.02
    confidence_levels: List[float] = field(default_factory=lambda: [0.95, 0.99])

    def __post_init__(self):
        if self.correlation_matrix is None:
            n = len(self.assets)
            self.correlation_matrix = np.eye(n)


@dataclass
class SimulationResult:
    """Results from portfolio simulation."""
    portfolio_returns: np.ndarray
    final_values: np.ndarray
    var: Dict[float, float]
    cvar: Dict[float, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    simulation_time_ms: float
    num_simulations: int
    gpu_used: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "var": {f"{int(k*100)}%": v for k, v in self.var.items()},
            "cvar": {f"{int(k*100)}%": v for k, v in self.cvar.items()},
            "num_simulations": self.num_simulations,
            "simulation_time_ms": self.simulation_time_ms,
            "gpu_used": self.gpu_used,
        }


class PortfolioSimulator:
    """GPU-accelerated Monte Carlo portfolio simulation."""

    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.xp = cp if self.use_gpu else np

        if self.use_gpu:
            LOGGER.info("Using GPU acceleration (CuPy)")
        else:
            LOGGER.info("Using CPU (NumPy)")

    def simulate(
        self,
        config: PortfolioConfig,
        num_simulations: int = 100000,
        initial_value: float = 1000000.0,
    ) -> SimulationResult:
        """Run Monte Carlo simulation for portfolio."""
        start_time = time.time()
        xp = self.xp

        n_assets = len(config.assets)
        n_days = config.time_horizon_days

        # Convert to arrays
        weights = xp.array([a.weight for a in config.assets])
        returns = xp.array([a.expected_return for a in config.assets])
        volatilities = xp.array([a.volatility for a in config.assets])
        corr_matrix = xp.array(config.correlation_matrix)

        # Daily parameters
        daily_returns = returns / 252
        daily_volatilities = volatilities / xp.sqrt(252)

        # Cholesky decomposition for correlated returns
        cov_matrix = xp.outer(daily_volatilities, daily_volatilities) * corr_matrix
        cholesky = xp.linalg.cholesky(cov_matrix)

        # Generate random returns
        random_normals = xp.random.standard_normal((num_simulations, n_days, n_assets))
        correlated_returns = xp.einsum('ijk,lk->ijl', random_normals, cholesky)

        # Add drift
        asset_returns = daily_returns + correlated_returns

        # Calculate portfolio returns
        portfolio_daily_returns = xp.sum(asset_returns * weights, axis=2)

        # Calculate cumulative returns
        cumulative_returns = xp.cumprod(1 + portfolio_daily_returns, axis=1)
        final_values = initial_value * cumulative_returns[:, -1]

        # Calculate portfolio total returns
        portfolio_returns = (final_values / initial_value) - 1

        # Convert to numpy for metrics calculation
        if self.use_gpu:
            portfolio_returns_np = cp.asnumpy(portfolio_returns)
            final_values_np = cp.asnumpy(final_values)
            cumulative_returns_np = cp.asnumpy(cumulative_returns)
        else:
            portfolio_returns_np = portfolio_returns
            final_values_np = final_values
            cumulative_returns_np = cumulative_returns

        # Calculate risk metrics
        var = {}
        cvar = {}
        for conf in config.confidence_levels:
            var_value = self._calculate_var(portfolio_returns_np, conf, initial_value)
            cvar_value = self._calculate_cvar(portfolio_returns_np, conf, initial_value)
            var[conf] = var_value
            cvar[conf] = cvar_value

        # Calculate portfolio statistics
        expected_return = float(np.mean(portfolio_returns_np))
        volatility = float(np.std(portfolio_returns_np))
        sharpe = (expected_return - config.risk_free_rate) / volatility if volatility > 0 else 0
        max_drawdown = self._calculate_max_drawdown(cumulative_returns_np)

        simulation_time = (time.time() - start_time) * 1000

        return SimulationResult(
            portfolio_returns=portfolio_returns_np,
            final_values=final_values_np,
            var=var,
            cvar=cvar,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            simulation_time_ms=simulation_time,
            num_simulations=num_simulations,
            gpu_used=self.use_gpu,
        )

    def _calculate_var(
        self,
        returns: np.ndarray,
        confidence: float,
        initial_value: float,
    ) -> float:
        """Calculate Value at Risk."""
        percentile = (1 - confidence) * 100
        var_return = np.percentile(returns, percentile)
        return float(-var_return * initial_value)

    def _calculate_cvar(
        self,
        returns: np.ndarray,
        confidence: float,
        initial_value: float,
    ) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        percentile = (1 - confidence) * 100
        var_return = np.percentile(returns, percentile)
        tail_returns = returns[returns <= var_return]
        if len(tail_returns) == 0:
            return 0.0
        cvar_return = np.mean(tail_returns)
        return float(-cvar_return * initial_value)

    def _calculate_max_drawdown(self, cumulative_returns: np.ndarray) -> float:
        """Calculate maximum drawdown across all simulations."""
        # Calculate running maximum
        running_max = np.maximum.accumulate(cumulative_returns, axis=1)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        return float(-max_drawdown)

    def stress_test(
        self,
        config: PortfolioConfig,
        scenarios: List[Dict[str, float]],
        initial_value: float = 1000000.0,
    ) -> List[Dict[str, Any]]:
        """Run stress test scenarios."""
        results = []

        for scenario in scenarios:
            # Modify asset returns based on scenario
            stressed_assets = []
            for asset in config.assets:
                shock = scenario.get(asset.symbol, scenario.get("market", 0))
                stressed_assets.append(Asset(
                    symbol=asset.symbol,
                    weight=asset.weight,
                    expected_return=asset.expected_return + shock,
                    volatility=asset.volatility * scenario.get("vol_multiplier", 1.0),
                ))

            stressed_config = PortfolioConfig(
                assets=stressed_assets,
                correlation_matrix=config.correlation_matrix,
                time_horizon_days=config.time_horizon_days,
                risk_free_rate=config.risk_free_rate,
            )

            sim_result = self.simulate(stressed_config, num_simulations=10000, initial_value=initial_value)

            results.append({
                "scenario": scenario.get("name", "unnamed"),
                "expected_return": sim_result.expected_return,
                "var_95": sim_result.var.get(0.95, 0),
                "max_drawdown": sim_result.max_drawdown,
            })

        return results


def create_sample_portfolio() -> PortfolioConfig:
    """Create a sample diversified portfolio."""
    assets = [
        Asset("SPY", 0.40, 0.10, 0.18),   # S&P 500
        Asset("AGG", 0.25, 0.04, 0.05),   # Bonds
        Asset("VWO", 0.15, 0.12, 0.25),   # Emerging Markets
        Asset("GLD", 0.10, 0.06, 0.15),   # Gold
        Asset("VNQ", 0.10, 0.08, 0.20),   # REITs
    ]

    correlation = np.array([
        [1.00, 0.10, 0.75, 0.05, 0.60],
        [0.10, 1.00, 0.15, 0.25, 0.20],
        [0.75, 0.15, 1.00, 0.10, 0.50],
        [0.05, 0.25, 0.10, 1.00, 0.15],
        [0.60, 0.20, 0.50, 0.15, 1.00],
    ])

    return PortfolioConfig(assets=assets, correlation_matrix=correlation)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    portfolio = create_sample_portfolio()
    simulator = PortfolioSimulator(use_gpu=True)

    print("Running portfolio simulation...")
    result = simulator.simulate(portfolio, num_simulations=100000)

    print(f"\nPortfolio Statistics:")
    print(f"  Expected Return: {result.expected_return:.2%}")
    print(f"  Volatility: {result.volatility:.2%}")
    print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"  Max Drawdown: {result.max_drawdown:.2%}")
    print(f"\nRisk Metrics:")
    for conf, var in result.var.items():
        print(f"  VaR ({int(conf*100)}%): ${var:,.0f}")
    for conf, cvar in result.cvar.items():
        print(f"  CVaR ({int(conf*100)}%): ${cvar:,.0f}")
    print(f"\nSimulation completed in {result.simulation_time_ms:.2f}ms")
    print(f"GPU used: {result.gpu_used}")
