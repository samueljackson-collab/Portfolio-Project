"""Quantum-assisted portfolio optimization demo."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

try:
    from qiskit import Aer
    from qiskit.algorithms import VQE
    from qiskit.circuit.library import TwoLocal
    from qiskit.opflow import PauliSumOp
    from qiskit.utils import QuantumInstance
except ImportError:  # pragma: no cover - optional dependency for documentation
    Aer = VQE = TwoLocal = PauliSumOp = QuantumInstance = None  # type: ignore

LOGGER = logging.getLogger(__name__)


@dataclass
class Asset:
    symbol: str
    expected_return: float
    risk_weight: float


def build_hamiltonian(assets: List[Asset]) -> PauliSumOp:
    num_assets = len(assets)
    pauli_terms = []
    for idx, asset in enumerate(assets):
        z_term = (asset.risk_weight / 2) * (
            PauliSumOp.from_list(
                [("I" * idx + "Z" + "I" * (num_assets - idx - 1), 1.0)]
            )
        )
        pauli_terms.append(z_term)
    return sum(pauli_terms)


def optimize_portfolio(assets: List[Asset]) -> None:
    if VQE is None:
        LOGGER.warning("Qiskit not installed; falling back to classical strategy")
        greedy = sorted(
            assets,
            key=lambda asset: asset.expected_return / asset.risk_weight,
            reverse=True,
        )
        LOGGER.info("Selected allocation: %s", [asset.symbol for asset in greedy[:3]])
        return

    hamiltonian = build_hamiltonian(assets)
    ansatz = TwoLocal(rotation_blocks="ry", entanglement_blocks="cz", reps=1)
    optimizer = VQE(
        ansatz,
        quantum_instance=QuantumInstance(Aer.get_backend("statevector_simulator")),
    )
    result = optimizer.compute_minimum_eigenvalue(hamiltonian)
    LOGGER.info("Optimal value: %s", result.eigenvalue)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    assets = [
        Asset("AWS", 0.12, 0.07),
        Asset("GOOG", 0.10, 0.05),
        Asset("MSFT", 0.09, 0.04),
        Asset("TSLA", 0.18, 0.12),
    ]
    optimize_portfolio(assets)
