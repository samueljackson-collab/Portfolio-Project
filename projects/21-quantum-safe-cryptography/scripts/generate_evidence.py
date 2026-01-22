"""Generate protocol logs, benchmarks, and charts for PQC vs classical flows."""
from __future__ import annotations

import csv
import json
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519

from src.hybrid_exchange import HybridKeyExchange
from src.pqc_provider import (
    KEMAlgorithm,
    SignatureAlgorithm,
    create_kem_provider,
    create_signature_provider,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = PROJECT_ROOT / "evidence"


@dataclass
class BenchmarkResult:
    name: str
    category: str
    mean_ms: float
    median_ms: float
    p95_ms: float
    payload_bytes: int
    public_key_bytes: int
    signature_bytes: int | None = None
    ciphertext_bytes: int | None = None


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * percentile)
    return sorted_values[index]


def _benchmark(func, iterations: int) -> list[float]:
    durations = []
    for _ in range(iterations):
        start = perf_counter()
        func()
        durations.append((perf_counter() - start) * 1000)
    return durations


def run_protocol_logs(log_path: Path) -> dict[str, int]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("protocol")
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Starting protocol flow capture")
    exchange = HybridKeyExchange()
    alice = exchange.generate_keypair()
    bob = exchange.generate_keypair()
    logger.info("Alice key_id=%s pqc_public=%d classical_public=%d", alice.key_id,
                len(alice.pqc_keypair.public_key), len(alice.classical_public))
    logger.info("Bob key_id=%s pqc_public=%d classical_public=%d", bob.key_id,
                len(bob.pqc_keypair.public_key), len(bob.classical_public))

    encapsulation, alice_shared = exchange.encapsulate(
        bob.pqc_keypair.public_key, bob.classical_public
    )
    bob_shared = exchange.decapsulate(bob, encapsulation)
    logger.info("Encapsulation pqc_ciphertext=%d classical_public=%d", len(encapsulation.pqc_ciphertext),
                len(encapsulation.classical_public))
    logger.info("Derived shared secret match=%s length=%d", alice_shared == bob_shared, len(alice_shared))

    signature_provider = create_signature_provider(SignatureAlgorithm.DILITHIUM3)
    signer_keys = signature_provider.generate_keypair()
    message = b"quantum-safe signing flow evidence"
    signature_result = signature_provider.sign(signer_keys.secret_key, message)
    verified = signature_provider.verify(
        signer_keys.public_key, message, signature_result.signature
    )
    logger.info("Signature algorithm=%s public_key=%d signature=%d verified=%s",
                signature_provider.algorithm, len(signer_keys.public_key),
                len(signature_result.signature), verified)
    logger.info("Protocol flow capture complete")

    handler.close()
    logger.removeHandler(handler)

    return {
        "hybrid_pqc_public": len(alice.pqc_keypair.public_key),
        "hybrid_classical_public": len(alice.classical_public),
        "hybrid_pqc_ciphertext": len(encapsulation.pqc_ciphertext),
        "hybrid_classical_ephemeral": len(encapsulation.classical_public),
        "signature_public": len(signer_keys.public_key),
        "signature_bytes": len(signature_result.signature),
    }


def benchmark_key_exchange(iterations: int) -> tuple[BenchmarkResult, BenchmarkResult]:
    def classical_flow():
        priv_a = x25519.X25519PrivateKey.generate()
        priv_b = x25519.X25519PrivateKey.generate()
        pub_a = priv_a.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        pub_b = priv_b.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        shared_a = priv_a.exchange(x25519.X25519PublicKey.from_public_bytes(pub_b))
        shared_b = priv_b.exchange(x25519.X25519PublicKey.from_public_bytes(pub_a))
        if shared_a != shared_b:
            raise RuntimeError("Classical ECDH mismatch")

    def pqc_flow():
        provider = create_kem_provider(KEMAlgorithm.KYBER768)
        keypair = provider.generate_keypair()
        encapsulation = provider.encapsulate(keypair.public_key)
        shared = provider.decapsulate(keypair.secret_key, encapsulation.ciphertext)
        if shared != encapsulation.shared_secret:
            raise RuntimeError("PQC KEM mismatch")

    classical_samples = _benchmark("classical-ecdh", classical_flow, iterations)
    pqc_samples = _benchmark("pqc-kem", pqc_flow, iterations)

    pub_a = x25519.X25519PrivateKey.generate().public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pub_b = x25519.X25519PrivateKey.generate().public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    classical_payload = len(pub_a) + len(pub_b)

    pqc_provider = create_kem_provider(KEMAlgorithm.KYBER768)
    pqc_keys = pqc_provider.generate_keypair()
    pqc_encap = pqc_provider.encapsulate(pqc_keys.public_key)
    pqc_payload = len(pqc_keys.public_key) + len(pqc_encap.ciphertext)

    classical_result = BenchmarkResult(
        name="Classical X25519 key exchange",
        category="key_exchange",
        mean_ms=statistics.mean(classical_samples),
        median_ms=statistics.median(classical_samples),
        p95_ms=_percentile(classical_samples, 0.95),
        payload_bytes=classical_payload,
        public_key_bytes=len(pub_a),
    )

    pqc_result = BenchmarkResult(
        name=f"PQC {pqc_provider.algorithm} KEM",
        category="key_exchange",
        mean_ms=statistics.mean(pqc_samples),
        median_ms=statistics.median(pqc_samples),
        p95_ms=_percentile(pqc_samples, 0.95),
        payload_bytes=pqc_payload,
        public_key_bytes=len(pqc_keys.public_key),
        ciphertext_bytes=len(pqc_encap.ciphertext),
    )

    return classical_result, pqc_result


def benchmark_signatures(iterations: int) -> tuple[BenchmarkResult, BenchmarkResult]:
    message = b"benchmark signing flow"

    def classical_flow():
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        sig = priv.sign(message)
        pub.verify(sig, message)

    def pqc_flow():
        provider = create_signature_provider(SignatureAlgorithm.DILITHIUM3)
        keys = provider.generate_keypair()
        sig = provider.sign(keys.secret_key, message)
        if not provider.verify(keys.public_key, message, sig.signature):
            raise RuntimeError("PQC signature verify failed")

    classical_samples = _benchmark("classical-ed25519", classical_flow, iterations)
    pqc_samples = _benchmark("pqc-sign", pqc_flow, iterations)

    classical_key = ed25519.Ed25519PrivateKey.generate()
    classical_pub = classical_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    classical_sig = classical_key.sign(message)

    signature_provider = create_signature_provider(SignatureAlgorithm.DILITHIUM3)
    pqc_keys = signature_provider.generate_keypair()
    pqc_sig = signature_provider.sign(pqc_keys.secret_key, message)

    classical_result = BenchmarkResult(
        name="Classical Ed25519 signature",
        category="signature",
        mean_ms=statistics.mean(classical_samples),
        median_ms=statistics.median(classical_samples),
        p95_ms=_percentile(classical_samples, 0.95),
        payload_bytes=len(classical_sig),
        public_key_bytes=len(classical_pub),
        signature_bytes=len(classical_sig),
    )

    pqc_result = BenchmarkResult(
        name=f"PQC {signature_provider.algorithm} signature",
        category="signature",
        mean_ms=statistics.mean(pqc_samples),
        median_ms=statistics.median(pqc_samples),
        p95_ms=_percentile(pqc_samples, 0.95),
        payload_bytes=len(pqc_sig.signature),
        public_key_bytes=len(pqc_keys.public_key),
        signature_bytes=len(pqc_sig.signature),
    )

    return classical_result, pqc_result


def write_benchmarks(results: list[BenchmarkResult], output_dir: Path) -> None:
    json_path = output_dir / "performance-benchmarks.json"
    csv_path = output_dir / "performance-benchmarks.csv"

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "results": [asdict(result) for result in results],
    }
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[f.name for f in fields(BenchmarkResult)],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def render_charts(results: list[BenchmarkResult], output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    key_exchange = [r for r in results if r.category == "key_exchange"]
    signature = [r for r in results if r.category == "signature"]

    def _plot(metric: str, filename: str, ylabel: str) -> None:
        labels = ["Key Exchange", "Signature"]
        classical = [
            key_exchange[0].__dict__[metric],
            signature[0].__dict__[metric],
        ]
        pqc = [
            key_exchange[1].__dict__[metric],
            signature[1].__dict__[metric],
        ]

        x_positions = range(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar([x - width / 2 for x in x_positions], classical, width, label="Classical")
        ax.bar([x + width / 2 for x in x_positions], pqc, width, label="PQC")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Classical vs PQC {ylabel}")
        ax.set_xticks(list(x_positions))
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        fig.tight_layout()
        fig.savefig(output_dir / filename, dpi=150)
        plt.close(fig)

    _plot("mean_ms", "pqc_vs_classical_latency.png", "Mean latency (ms)")
    _plot("payload_bytes", "pqc_vs_classical_payload.png", "Payload size (bytes)")


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    protocol_log_path = EVIDENCE_DIR / "protocol-logs.txt"
    protocol_sizes = run_protocol_logs(protocol_log_path)

    benchmark_results = []
    benchmark_results.extend(benchmark_key_exchange(iterations=50))
    benchmark_results.extend(benchmark_signatures(iterations=50))

    write_benchmarks(benchmark_results, EVIDENCE_DIR)
    render_charts(benchmark_results, EVIDENCE_DIR)

    summary_path = EVIDENCE_DIR / "benchmark-summary.md"
    summary_lines = [
        "# Benchmark Summary",
        "",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "## Protocol Payload Sizes",
        "",
        f"- Hybrid PQC public key: {protocol_sizes['hybrid_pqc_public']} bytes",
        f"- Hybrid classical public key: {protocol_sizes['hybrid_classical_public']} bytes",
        f"- Hybrid PQC ciphertext: {protocol_sizes['hybrid_pqc_ciphertext']} bytes",
        f"- Hybrid classical ephemeral public key: {protocol_sizes['hybrid_classical_ephemeral']} bytes",
        f"- Signature public key: {protocol_sizes['signature_public']} bytes",
        f"- Signature bytes: {protocol_sizes['signature_bytes']} bytes",
        "",
        "## Benchmark Averages",
        "",
    ]

    for result in benchmark_results:
        summary_lines.append(
            f"- {result.name}: {result.mean_ms:.3f} ms mean, "
            f"{result.payload_bytes} bytes payload"
        )

    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
