"""A/B testing framework for model comparison and deployment."""
from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import mlflow
import numpy as np
from scipy import stats
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ABTestConfig:
    """Configuration for A/B test."""
    test_name: str
    model_a_uri: str  # MLflow model URI
    model_b_uri: str  # MLflow model URI
    traffic_split: float = 0.5  # % of traffic to model B
    min_samples: int = 100  # Minimum samples before analysis
    confidence_level: float = 0.95
    metric: str = "accuracy"  # Metric to optimize


@dataclass
class ABTestResult:
    """Results of A/B test."""
    model_a_metric: float
    model_b_metric: float
    p_value: float
    is_significant: bool
    winner: str  # "A", "B", or "tie"
    sample_size_a: int
    sample_size_b: int
    improvement: float  # % improvement of B over A


class ABTestingFramework:
    """Framework for A/B testing models in production."""

    def __init__(self, config: ABTestConfig):
        """
        Initialize A/B testing framework.

        Args:
            config: A/B test configuration
        """
        self.config = config

        # Load models
        logger.info(f"Loading model A from {config.model_a_uri}")
        self.model_a = mlflow.pyfunc.load_model(config.model_a_uri)

        logger.info(f"Loading model B from {config.model_b_uri}")
        self.model_b = mlflow.pyfunc.load_model(config.model_b_uri)

        # Initialize result tracking
        self.results_a: List[Dict[str, Any]] = []
        self.results_b: List[Dict[str, Any]] = []

        logger.info(f"A/B test '{config.test_name}' initialized")

    def route_request(self, request_id: str = None) -> str:
        """
        Route request to model A or B based on traffic split.

        Args:
            request_id: Optional request ID for deterministic routing

        Returns:
            Model variant ("A" or "B")
        """
        if request_id:
            # Deterministic routing based on request ID hash
            hash_val = hash(request_id)
            variant = "B" if (hash_val % 100) < (self.config.traffic_split * 100) else "A"
        else:
            # Random routing
            variant = "B" if random.random() < self.config.traffic_split else "A"

        return variant

    def predict(
        self,
        features: np.ndarray,
        request_id: Optional[str] = None,
        true_label: Optional[int] = None
    ) -> Tuple[np.ndarray, str]:
        """
        Make prediction using A/B test routing.

        Args:
            features: Input features
            request_id: Optional request ID
            true_label: Optional ground truth for tracking

        Returns:
            Tuple of (predictions, variant)
        """
        # Route to model
        variant = self.route_request(request_id)

        # Make prediction
        if variant == "A":
            predictions = self.model_a.predict(features)
        else:
            predictions = self.model_b.predict(features)

        # Track result if ground truth provided
        if true_label is not None:
            result = {
                'timestamp': datetime.now().isoformat(),
                'prediction': int(predictions[0]) if len(predictions) == 1 else predictions.tolist(),
                'true_label': int(true_label),
                'correct': int(predictions[0]) == true_label if len(predictions) == 1 else None
            }

            if variant == "A":
                self.results_a.append(result)
            else:
                self.results_b.append(result)

        return predictions, variant

    def calculate_metric(self, results: List[Dict[str, Any]]) -> float:
        """
        Calculate specified metric from results.

        Args:
            results: List of prediction results

        Returns:
            Metric value
        """
        if not results:
            return 0.0

        if self.config.metric == "accuracy":
            correct = sum(1 for r in results if r.get('correct'))
            return correct / len(results)

        # Add more metrics as needed
        return 0.0

    def analyze_results(self) -> ABTestResult:
        """
        Analyze A/B test results using statistical testing.

        Returns:
            A/B test results
        """
        # Calculate metrics
        metric_a = self.calculate_metric(self.results_a)
        metric_b = self.calculate_metric(self.results_b)

        # Get sample sizes
        n_a = len(self.results_a)
        n_b = len(self.results_b)

        logger.info(f"Model A: {metric_a:.4f} (n={n_a})")
        logger.info(f"Model B: {metric_b:.4f} (n={n_b})")

        # Check minimum sample size
        if n_a < self.config.min_samples or n_b < self.config.min_samples:
            logger.warning(
                f"Insufficient samples: A={n_a}, B={n_b}, "
                f"minimum={self.config.min_samples}"
            )

        # Perform statistical test (two-proportion z-test)
        successes_a = sum(1 for r in self.results_a if r.get('correct'))
        successes_b = sum(1 for r in self.results_b if r.get('correct'))

        # Calculate pooled proportion
        p_pool = (successes_a + successes_b) / (n_a + n_b)

        # Calculate standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))

        # Calculate z-score
        z_score = (metric_b - metric_a) / se if se > 0 else 0

        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        # Determine significance
        is_significant = p_value < (1 - self.config.confidence_level)

        # Determine winner
        if is_significant:
            winner = "B" if metric_b > metric_a else "A"
        else:
            winner = "tie"

        # Calculate improvement
        improvement = ((metric_b - metric_a) / metric_a * 100) if metric_a > 0 else 0

        result = ABTestResult(
            model_a_metric=metric_a,
            model_b_metric=metric_b,
            p_value=p_value,
            is_significant=is_significant,
            winner=winner,
            sample_size_a=n_a,
            sample_size_b=n_b,
            improvement=improvement
        )

        logger.info(f"Winner: {winner}")
        logger.info(f"P-value: {p_value:.4f}")
        logger.info(f"Improvement: {improvement:+.2f}%")

        return result

    def get_recommendation(self) -> str:
        """
        Get deployment recommendation based on test results.

        Returns:
            Recommendation string
        """
        result = self.analyze_results()

        if result.sample_size_a < self.config.min_samples or \
           result.sample_size_b < self.config.min_samples:
            return "CONTINUE_TEST: Insufficient samples for conclusive results"

        if not result.is_significant:
            return "KEEP_A: No significant difference detected"

        if result.winner == "B":
            if result.improvement >= 5:  # 5% improvement threshold
                return "DEPLOY_B: Model B shows significant improvement"
            else:
                return "KEEP_A: Improvement not substantial enough"
        elif result.winner == "A":
            return "KEEP_A: Model A performs better"
        else:
            return "KEEP_A: No clear winner"

    def export_results(self, output_path: str):
        """
        Export test results to JSON file.

        Args:
            output_path: Path to output file
        """
        result = self.analyze_results()

        data = {
            'config': asdict(self.config),
            'results': asdict(result),
            'recommendation': self.get_recommendation(),
            'timestamp': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Results exported to {output_path}")


class ABTestManager:
    """Manage multiple A/B tests."""

    def __init__(self):
        """Initialize A/B test manager."""
        self.active_tests: Dict[str, ABTestingFramework] = {}

    def create_test(self, config: ABTestConfig) -> ABTestingFramework:
        """
        Create a new A/B test.

        Args:
            config: Test configuration

        Returns:
            A/B testing framework instance
        """
        if config.test_name in self.active_tests:
            raise ValueError(f"Test '{config.test_name}' already exists")

        test = ABTestingFramework(config)
        self.active_tests[config.test_name] = test

        logger.info(f"Created A/B test: {config.test_name}")

        return test

    def get_test(self, test_name: str) -> ABTestingFramework:
        """
        Get existing A/B test.

        Args:
            test_name: Name of test

        Returns:
            A/B testing framework instance
        """
        if test_name not in self.active_tests:
            raise ValueError(f"Test '{test_name}' not found")

        return self.active_tests[test_name]

    def list_tests(self) -> List[str]:
        """
        List all active tests.

        Returns:
            List of test names
        """
        return list(self.active_tests.keys())

    def stop_test(self, test_name: str) -> ABTestResult:
        """
        Stop a test and get final results.

        Args:
            test_name: Name of test

        Returns:
            Final test results
        """
        if test_name not in self.active_tests:
            raise ValueError(f"Test '{test_name}' not found")

        test = self.active_tests[test_name]
        result = test.analyze_results()

        # Remove from active tests
        del self.active_tests[test_name]

        logger.info(f"Stopped test: {test_name}")

        return result


def main():
    """Example usage of A/B testing framework."""
    # Example configuration
    config = ABTestConfig(
        test_name="rf_vs_gb_classifier",
        model_a_uri="models:/random_forest_classifier/1",
        model_b_uri="models:/gradient_boosting_classifier/1",
        traffic_split=0.5,
        min_samples=100,
        confidence_level=0.95,
        metric="accuracy"
    )

    # Create A/B test
    ab_test = ABTestingFramework(config)

    # Simulate predictions (in production, this would be real traffic)
    logger.info("Simulating predictions...")

    for i in range(200):
        # Generate sample data
        features = np.random.randn(1, 20)
        true_label = random.randint(0, 1)

        # Make prediction
        predictions, variant = ab_test.predict(
            features,
            request_id=f"req_{i}",
            true_label=true_label
        )

    # Analyze results
    result = ab_test.analyze_results()

    print("\n" + "="*60)
    print("A/B TEST RESULTS")
    print("="*60)
    print(f"Model A Metric: {result.model_a_metric:.4f} (n={result.sample_size_a})")
    print(f"Model B Metric: {result.model_b_metric:.4f} (n={result.sample_size_b})")
    print(f"P-value: {result.p_value:.4f}")
    print(f"Significant: {result.is_significant}")
    print(f"Winner: {result.winner}")
    print(f"Improvement: {result.improvement:+.2f}%")
    print(f"\nRecommendation: {ab_test.get_recommendation()}")
    print("="*60)

    # Export results
    ab_test.export_results("ab_test_results.json")


if __name__ == "__main__":
    main()
