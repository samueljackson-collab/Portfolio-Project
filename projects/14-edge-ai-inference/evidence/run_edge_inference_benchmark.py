"""Simulate edge inference workloads and capture latency/throughput metrics."""
from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class DeviceProfile:
    name: str
    target_latency_ms: float
    power_watts: float
    matrix_size: int


@dataclass
class BenchmarkResult:
    name: str
    power_watts: float
    target_latency_ms: float
    runs: int
    p50_ms: float
    p95_ms: float
    avg_ms: float
    throughput_ips: float
    energy_j_per_inf: float


def _simulate_inference(matrix_size: int) -> None:
    """Perform a deterministic matrix multiply to emulate inference work."""
    rng = np.random.default_rng(42)
    a = rng.random((matrix_size, matrix_size), dtype=np.float32)
    b = rng.random((matrix_size, matrix_size), dtype=np.float32)
    _ = a @ b


def run_profile(profile: DeviceProfile, runs: int, warmups: int = 5) -> BenchmarkResult:
    latencies_ms: list[float] = []
    for _ in range(warmups):
        _simulate_inference(profile.matrix_size)

    for _ in range(runs):
        start = time.perf_counter()
        _simulate_inference(profile.matrix_size)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms < profile.target_latency_ms:
            time.sleep((profile.target_latency_ms - elapsed_ms) / 1000)
            elapsed_ms = profile.target_latency_ms
        latencies_ms.append(elapsed_ms)

    latencies = np.array(latencies_ms)
    p50_ms = float(np.percentile(latencies, 50))
    p95_ms = float(np.percentile(latencies, 95))
    avg_ms = float(np.mean(latencies))
    total_time_s = float(np.sum(latencies) / 1000)
    throughput_ips = runs / total_time_s if total_time_s > 0 else 0.0
    energy_j_per_inf = profile.power_watts * (avg_ms / 1000)

    return BenchmarkResult(
        name=profile.name,
        power_watts=profile.power_watts,
        target_latency_ms=profile.target_latency_ms,
        runs=runs,
        p50_ms=p50_ms,
        p95_ms=p95_ms,
        avg_ms=avg_ms,
        throughput_ips=throughput_ips,
        energy_j_per_inf=energy_j_per_inf,
    )


def save_results(results: Iterable[BenchmarkResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    payload = {
        "timestamp": timestamp,
        "profiles": [result.__dict__ for result in results],
    }
    (output_dir / "metrics.json").write_text(json.dumps(payload, indent=2))

    with (output_dir / "metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(results[0].__dict__.keys()) if results else [],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def plot_latency(results: Iterable[BenchmarkResult], output_dir: Path) -> None:
    names = [result.name for result in results]
    p50 = [result.p50_ms for result in results]
    p95 = [result.p95_ms for result in results]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - width / 2, p50, width, label="p50 latency")
    ax.bar(x + width / 2, p95, width, label="p95 latency")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Edge Inference Latency")
    ax.set_xticks(x, names)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(output_dir / "latency_p50_p95.svg")
    plt.close(fig)


def plot_throughput(results: Iterable[BenchmarkResult], output_dir: Path) -> None:
    names = [result.name for result in results]
    throughput = [result.throughput_ips for result in results]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.bar(names, throughput, color="#4c78a8")
    ax.set_ylabel("Inferences per second")
    ax.set_title("Edge Inference Throughput")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(output_dir / "throughput_ips.svg")
    plt.close(fig)


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    profiles = [
        DeviceProfile(
            name="Jetson Nano (sim)",
            target_latency_ms=45.0,
            power_watts=5.0,
            matrix_size=96,
        ),
        DeviceProfile(
            name="Jetson Orin (sim)",
            target_latency_ms=12.0,
            power_watts=15.0,
            matrix_size=128,
        ),
        DeviceProfile(
            name="Coral Edge TPU (sim)",
            target_latency_ms=20.0,
            power_watts=6.0,
            matrix_size=112,
        ),
    ]

    results = [run_profile(profile, runs=60) for profile in profiles]
    save_results(results, output_dir)
    plot_latency(results, output_dir)
    plot_throughput(results, output_dir)


if __name__ == "__main__":
    main()
