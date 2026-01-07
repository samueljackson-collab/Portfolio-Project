"""Configuration management for Quantum Portfolio Optimizer."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import yaml


class SolverType(Enum):
    """Available solver types."""
    QUANTUM_VQE = "quantum_vqe"
    QUANTUM_QAOA = "quantum_qaoa"
    SIMULATED_ANNEALING = "simulated_annealing"
    GENETIC_ALGORITHM = "genetic_algorithm"
    HYBRID = "hybrid"
    CLASSICAL_GREEDY = "classical_greedy"


class BackendType(Enum):
    """Quantum backend providers."""
    IBM_QUANTUM = "ibm_quantum"
    AWS_BRAKET = "aws_braket"
    LOCAL_SIMULATOR = "local_simulator"
    MOCK = "mock"


@dataclass
class QuantumConfig:
    """Quantum solver configuration."""
    backend: BackendType = BackendType.LOCAL_SIMULATOR
    num_qubits: int = 8
    shots: int = 1024
    optimization_level: int = 3
    max_circuit_depth: int = 50
    ibm_token: Optional[str] = None
    aws_region: str = "us-east-1"

    def __post_init__(self):
        if self.ibm_token is None:
            self.ibm_token = os.environ.get("IBM_QUANTUM_TOKEN")


@dataclass
class ClassicalConfig:
    """Classical solver configuration."""
    solver_type: SolverType = SolverType.SIMULATED_ANNEALING
    max_iterations: int = 10000
    temperature_initial: float = 100.0
    temperature_final: float = 0.01
    cooling_rate: float = 0.995
    population_size: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    num_workers: int = 4


@dataclass
class PortfolioConstraints:
    """Portfolio optimization constraints."""
    min_assets: int = 3
    max_assets: int = 20
    min_weight: float = 0.01
    max_weight: float = 0.40
    target_return: Optional[float] = None
    max_risk: Optional[float] = None
    sector_limits: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate constraints and return list of errors."""
        errors = []
        if self.min_assets > self.max_assets:
            errors.append("min_assets cannot exceed max_assets")
        if self.min_weight > self.max_weight:
            errors.append("min_weight cannot exceed max_weight")
        if self.min_weight < 0 or self.max_weight > 1:
            errors.append("weights must be between 0 and 1")
        return errors


@dataclass
class AWSBatchConfig:
    """AWS Batch job configuration."""
    enabled: bool = False
    job_queue: str = "quantum-optimization-queue"
    job_definition: str = "quantum-optimizer-job"
    compute_environment: str = "quantum-compute-env"
    vcpus: int = 4
    memory: int = 8192
    timeout_seconds: int = 3600
    s3_bucket: str = ""

    def __post_init__(self):
        if not self.s3_bucket:
            self.s3_bucket = os.environ.get("QUANTUM_S3_BUCKET", "quantum-results")


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    log_level: str = "INFO"
    structured_logging: bool = True
    trace_circuits: bool = False
    export_results_to_s3: bool = False


@dataclass
class AppConfig:
    """Main application configuration."""
    solver_type: SolverType = SolverType.HYBRID
    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    classical: ClassicalConfig = field(default_factory=ClassicalConfig)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    aws_batch: AWSBatchConfig = field(default_factory=AWSBatchConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "AppConfig":
        """Load configuration from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            solver_type=SolverType(data.get("solver_type", "hybrid")),
            quantum=QuantumConfig(
                backend=BackendType(data.get("quantum", {}).get("backend", "local_simulator")),
                **{k: v for k, v in data.get("quantum", {}).items() if k != "backend"}
            ),
            classical=ClassicalConfig(
                solver_type=SolverType(data.get("classical", {}).get("solver_type", "simulated_annealing")),
                **{k: v for k, v in data.get("classical", {}).items() if k != "solver_type"}
            ),
            constraints=PortfolioConstraints(**data.get("constraints", {})),
            aws_batch=AWSBatchConfig(**data.get("aws_batch", {})),
            monitoring=MonitoringConfig(**data.get("monitoring", {})),
        )

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        return cls(
            solver_type=SolverType(os.environ.get("SOLVER_TYPE", "hybrid")),
            quantum=QuantumConfig(
                backend=BackendType(os.environ.get("QUANTUM_BACKEND", "local_simulator")),
                num_qubits=int(os.environ.get("QUANTUM_QUBITS", "8")),
                shots=int(os.environ.get("QUANTUM_SHOTS", "1024")),
            ),
            classical=ClassicalConfig(
                max_iterations=int(os.environ.get("CLASSICAL_MAX_ITER", "10000")),
            ),
            aws_batch=AWSBatchConfig(
                enabled=os.environ.get("AWS_BATCH_ENABLED", "false").lower() == "true",
            ),
            monitoring=MonitoringConfig(
                log_level=os.environ.get("LOG_LEVEL", "INFO"),
            ),
        )

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        data = {
            "solver_type": self.solver_type.value,
            "quantum": {
                "backend": self.quantum.backend.value,
                "num_qubits": self.quantum.num_qubits,
                "shots": self.quantum.shots,
                "optimization_level": self.quantum.optimization_level,
                "max_circuit_depth": self.quantum.max_circuit_depth,
                "aws_region": self.quantum.aws_region,
            },
            "classical": {
                "solver_type": self.classical.solver_type.value,
                "max_iterations": self.classical.max_iterations,
                "temperature_initial": self.classical.temperature_initial,
                "temperature_final": self.classical.temperature_final,
                "cooling_rate": self.classical.cooling_rate,
                "population_size": self.classical.population_size,
                "mutation_rate": self.classical.mutation_rate,
                "crossover_rate": self.classical.crossover_rate,
            },
            "constraints": {
                "min_assets": self.constraints.min_assets,
                "max_assets": self.constraints.max_assets,
                "min_weight": self.constraints.min_weight,
                "max_weight": self.constraints.max_weight,
                "target_return": self.constraints.target_return,
                "max_risk": self.constraints.max_risk,
                "sector_limits": self.constraints.sector_limits,
            },
            "aws_batch": {
                "enabled": self.aws_batch.enabled,
                "job_queue": self.aws_batch.job_queue,
                "job_definition": self.aws_batch.job_definition,
                "s3_bucket": self.aws_batch.s3_bucket,
            },
            "monitoring": {
                "prometheus_enabled": self.monitoring.prometheus_enabled,
                "log_level": self.monitoring.log_level,
                "structured_logging": self.monitoring.structured_logging,
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)
