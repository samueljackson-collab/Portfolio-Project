"""GPU-accelerated Monte Carlo simulation using CuPy."""

from __future__ import annotations

import argparse
import cupy as cp


def simulate(iterations: int) -> float:
    random_values = cp.random.standard_normal(iterations)
    payoff = cp.maximum(random_values, 0)
    return float(payoff.mean())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1_000_000)
    args = parser.parse_args()
    result = simulate(args.iterations)
    print(f"Expected payoff: {result:.4f}")
