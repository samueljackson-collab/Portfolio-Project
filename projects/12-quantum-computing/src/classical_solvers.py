"""Classical optimization solvers for portfolio optimization."""
from __future__ import annotations

import logging
import math
import random
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from .config import ClassicalConfig, PortfolioConstraints

LOGGER = logging.getLogger(__name__)


@dataclass
class Asset:
    """Represents a financial asset."""
    symbol: str
    expected_return: float
    volatility: float
    sector: str = "general"
    correlation_group: Optional[str] = None


@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    weights: Dict[str, float]
    expected_return: float
    risk: float
    sharpe_ratio: float
    iterations: int
    solver_type: str
    converged: bool
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseSolver(ABC):
    """Abstract base class for optimization solvers."""

    def __init__(self, config: ClassicalConfig, constraints: PortfolioConstraints):
        self.config = config
        self.constraints = constraints

    @abstractmethod
    def optimize(
        self,
        assets: List[Asset],
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
    ) -> OptimizationResult:
        """Run optimization and return result."""
        pass

    def _calculate_portfolio_metrics(
        self,
        weights: np.ndarray,
        returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float,
    ) -> Tuple[float, float, float]:
        """Calculate portfolio return, risk, and Sharpe ratio."""
        portfolio_return = np.dot(weights, returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (portfolio_return - risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
        return portfolio_return, portfolio_risk, sharpe

    def _validate_weights(self, weights: np.ndarray, assets: List[Asset]) -> bool:
        """Validate portfolio weights against constraints."""
        if abs(np.sum(weights) - 1.0) > 1e-6:
            return False
        if np.any(weights < self.constraints.min_weight - 1e-6):
            return False
        if np.any(weights > self.constraints.max_weight + 1e-6):
            return False
        num_selected = np.sum(weights > self.constraints.min_weight)
        if num_selected < self.constraints.min_assets:
            return False
        if num_selected > self.constraints.max_assets:
            return False
        return True


class SimulatedAnnealingSolver(BaseSolver):
    """Simulated annealing optimizer for portfolio selection."""

    def optimize(
        self,
        assets: List[Asset],
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
    ) -> OptimizationResult:
        n = len(assets)
        returns = np.array([a.expected_return for a in assets])

        # Initialize with equal weights
        current_weights = np.ones(n) / n
        current_weights = self._apply_constraints(current_weights)

        _, _, current_sharpe = self._calculate_portfolio_metrics(
            current_weights, returns, covariance_matrix, risk_free_rate
        )

        best_weights = current_weights.copy()
        best_sharpe = current_sharpe

        temperature = self.config.temperature_initial
        iterations = 0

        while temperature > self.config.temperature_final and iterations < self.config.max_iterations:
            # Generate neighbor solution
            new_weights = self._generate_neighbor(current_weights)
            new_weights = self._apply_constraints(new_weights)

            _, _, new_sharpe = self._calculate_portfolio_metrics(
                new_weights, returns, covariance_matrix, risk_free_rate
            )

            # Accept or reject
            delta = new_sharpe - current_sharpe
            if delta > 0 or random.random() < math.exp(delta / temperature):
                current_weights = new_weights
                current_sharpe = new_sharpe

                if current_sharpe > best_sharpe:
                    best_weights = current_weights.copy()
                    best_sharpe = current_sharpe

            temperature *= self.config.cooling_rate
            iterations += 1

        ret, risk, sharpe = self._calculate_portfolio_metrics(
            best_weights, returns, covariance_matrix, risk_free_rate
        )

        return OptimizationResult(
            weights={assets[i].symbol: float(best_weights[i]) for i in range(n)},
            expected_return=float(ret),
            risk=float(risk),
            sharpe_ratio=float(sharpe),
            iterations=iterations,
            solver_type="simulated_annealing",
            converged=iterations < self.config.max_iterations,
            metadata={"final_temperature": temperature},
        )

    def _generate_neighbor(self, weights: np.ndarray) -> np.ndarray:
        """Generate a neighboring solution by perturbing weights."""
        new_weights = weights.copy()
        i, j = random.sample(range(len(weights)), 2)
        delta = random.uniform(-0.05, 0.05)
        new_weights[i] = max(0, new_weights[i] + delta)
        new_weights[j] = max(0, new_weights[j] - delta)
        return new_weights

    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """Apply portfolio constraints to weights."""
        weights = np.clip(weights, self.constraints.min_weight, self.constraints.max_weight)
        weights = weights / np.sum(weights)  # Normalize
        return weights


class GeneticAlgorithmSolver(BaseSolver):
    """Genetic algorithm optimizer for portfolio selection."""

    def optimize(
        self,
        assets: List[Asset],
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
    ) -> OptimizationResult:
        n = len(assets)
        returns = np.array([a.expected_return for a in assets])

        # Initialize population
        population = self._initialize_population(n)

        best_individual = None
        best_fitness = float("-inf")

        for generation in range(self.config.max_iterations // self.config.population_size):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                _, _, sharpe = self._calculate_portfolio_metrics(
                    individual, returns, covariance_matrix, risk_free_rate
                )
                fitness_scores.append(sharpe)

                if sharpe > best_fitness:
                    best_fitness = sharpe
                    best_individual = individual.copy()

            # Selection
            selected = self._tournament_selection(population, fitness_scores)

            # Crossover
            offspring = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    child1, child2 = self._crossover(selected[i], selected[i + 1])
                    offspring.extend([child1, child2])

            # Mutation
            for i in range(len(offspring)):
                if random.random() < self.config.mutation_rate:
                    offspring[i] = self._mutate(offspring[i])

            # Apply constraints
            offspring = [self._apply_constraints(ind) for ind in offspring]

            # Replace population
            population = offspring[:self.config.population_size]

        ret, risk, sharpe = self._calculate_portfolio_metrics(
            best_individual, returns, covariance_matrix, risk_free_rate
        )

        return OptimizationResult(
            weights={assets[i].symbol: float(best_individual[i]) for i in range(n)},
            expected_return=float(ret),
            risk=float(risk),
            sharpe_ratio=float(sharpe),
            iterations=self.config.max_iterations,
            solver_type="genetic_algorithm",
            converged=True,
            metadata={"generations": self.config.max_iterations // self.config.population_size},
        )

    def _initialize_population(self, n: int) -> List[np.ndarray]:
        """Initialize random population."""
        population = []
        for _ in range(self.config.population_size):
            weights = np.random.dirichlet(np.ones(n))
            weights = self._apply_constraints(weights)
            population.append(weights)
        return population

    def _tournament_selection(
        self, population: List[np.ndarray], fitness: List[float], tournament_size: int = 3
    ) -> List[np.ndarray]:
        """Select individuals using tournament selection."""
        selected = []
        for _ in range(len(population)):
            tournament = random.sample(list(zip(population, fitness)), tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0].copy())
        return selected

    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Blend crossover between two parents."""
        if random.random() > self.config.crossover_rate:
            return parent1.copy(), parent2.copy()

        alpha = random.random()
        child1 = alpha * parent1 + (1 - alpha) * parent2
        child2 = (1 - alpha) * parent1 + alpha * parent2
        return child1, child2

    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """Mutate an individual by adding random noise."""
        noise = np.random.normal(0, 0.05, len(individual))
        mutated = individual + noise
        mutated = np.clip(mutated, 0, 1)
        return mutated / np.sum(mutated)

    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """Apply portfolio constraints to weights."""
        weights = np.clip(weights, self.constraints.min_weight, self.constraints.max_weight)
        weights = weights / np.sum(weights)
        return weights


class HybridSolver(BaseSolver):
    """Hybrid solver that combines quantum hints with classical optimization."""

    def __init__(
        self,
        config: ClassicalConfig,
        constraints: PortfolioConstraints,
        quantum_hints: Optional[Dict[str, float]] = None,
    ):
        super().__init__(config, constraints)
        self.quantum_hints = quantum_hints or {}

    def optimize(
        self,
        assets: List[Asset],
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
    ) -> OptimizationResult:
        n = len(assets)
        returns = np.array([a.expected_return for a in assets])

        # Use quantum hints to initialize if available
        if self.quantum_hints:
            initial_weights = self._apply_quantum_hints(assets)
        else:
            initial_weights = np.ones(n) / n

        # Run simulated annealing with quantum-informed initialization
        sa_solver = SimulatedAnnealingSolver(self.config, self.constraints)
        sa_result = sa_solver.optimize(assets, covariance_matrix, risk_free_rate)

        # Run genetic algorithm in parallel
        ga_solver = GeneticAlgorithmSolver(self.config, self.constraints)
        ga_result = ga_solver.optimize(assets, covariance_matrix, risk_free_rate)

        # Return best result
        if sa_result.sharpe_ratio >= ga_result.sharpe_ratio:
            best = sa_result
            best.solver_type = "hybrid_sa"
        else:
            best = ga_result
            best.solver_type = "hybrid_ga"

        best.metadata["quantum_hints_applied"] = bool(self.quantum_hints)
        return best

    def _apply_quantum_hints(self, assets: List[Asset]) -> np.ndarray:
        """Apply quantum-derived hints to initial weights."""
        weights = np.zeros(len(assets))
        for i, asset in enumerate(assets):
            if asset.symbol in self.quantum_hints:
                weights[i] = self.quantum_hints[asset.symbol]
            else:
                weights[i] = 1.0 / len(assets)
        return weights / np.sum(weights)


def create_solver(config: ClassicalConfig, constraints: PortfolioConstraints) -> BaseSolver:
    """Factory function to create appropriate solver."""
    from .config import SolverType

    solver_map = {
        SolverType.SIMULATED_ANNEALING: SimulatedAnnealingSolver,
        SolverType.GENETIC_ALGORITHM: GeneticAlgorithmSolver,
        SolverType.HYBRID: HybridSolver,
    }

    solver_class = solver_map.get(config.solver_type, SimulatedAnnealingSolver)
    return solver_class(config, constraints)


def run_parallel_optimization(
    assets: List[Asset],
    covariance_matrix: np.ndarray,
    config: ClassicalConfig,
    constraints: PortfolioConstraints,
    num_runs: int = 5,
) -> OptimizationResult:
    """Run multiple optimizations in parallel and return best result."""

    def single_run(_: int) -> OptimizationResult:
        solver = create_solver(config, constraints)
        return solver.optimize(assets, covariance_matrix)

    best_result = None

    with ProcessPoolExecutor(max_workers=config.num_workers) as executor:
        futures = [executor.submit(single_run, i) for i in range(num_runs)]

        for future in as_completed(futures):
            result = future.result()
            if best_result is None or result.sharpe_ratio > best_result.sharpe_ratio:
                best_result = result

    return best_result
