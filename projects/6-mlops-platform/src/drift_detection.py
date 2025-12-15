"""
Drift Detection Module for MLOps Platform.

Implements statistical drift detection for model monitoring using:
- Kolmogorov-Smirnov test for continuous features
- Chi-square test for categorical features
- Population Stability Index (PSI)
- Jensen-Shannon divergence
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DriftResult:
    """Results from drift detection analysis."""
    feature: str
    drift_detected: bool
    test_statistic: float
    p_value: float
    drift_score: float
    method: str
    threshold: float


class DriftDetector:
    """Detect statistical drift in model features and predictions."""

    def __init__(
        self,
        reference_data: pd.DataFrame,
        feature_columns: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        threshold: float = 0.05
    ):
        """
        Initialize drift detector with reference (baseline) data.

        Args:
            reference_data: Baseline dataset for comparison
            feature_columns: List of feature column names (auto-detect if None)
            categorical_features: List of categorical feature names
            threshold: P-value threshold for drift detection (default: 0.05)
        """
        self.reference_data = reference_data
        self.threshold = threshold

        # Auto-detect feature columns
        if feature_columns is None:
            self.feature_columns = [
                col for col in reference_data.columns
                if col not in ['target', 'timestamp', 'sample_id']
            ]
        else:
            self.feature_columns = feature_columns

        self.categorical_features = categorical_features or []

        # Compute reference statistics
        self.reference_stats = self._compute_statistics(reference_data)

        logger.info(f"DriftDetector initialized with {len(self.feature_columns)} features")
        logger.info(f"Threshold: {threshold}")

    def _compute_statistics(self, data: pd.DataFrame) -> Dict:
        """Compute statistical summaries for reference data."""
        stats_dict = {}

        for col in self.feature_columns:
            if col in self.categorical_features:
                # For categorical: frequency distribution
                stats_dict[col] = {
                    'type': 'categorical',
                    'value_counts': data[col].value_counts(normalize=True).to_dict(),
                    'unique_values': data[col].nunique()
                }
            else:
                # For continuous: descriptive statistics
                stats_dict[col] = {
                    'type': 'continuous',
                    'mean': data[col].mean(),
                    'std': data[col].std(),
                    'min': data[col].min(),
                    'max': data[col].max(),
                    'median': data[col].median(),
                    'q25': data[col].quantile(0.25),
                    'q75': data[col].quantile(0.75)
                }

        return stats_dict

    def ks_test(self, feature: str, current_data: pd.DataFrame) -> DriftResult:
        """Perform Kolmogorov-Smirnov test for continuous features."""
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()

        statistic, p_value = stats.ks_2samp(ref_values, curr_values)

        drift_detected = p_value < self.threshold

        return DriftResult(
            feature=feature,
            drift_detected=drift_detected,
            test_statistic=statistic,
            p_value=p_value,
            drift_score=statistic,
            method='ks_test',
            threshold=self.threshold
        )

    def chi_square_test(self, feature: str, current_data: pd.DataFrame) -> DriftResult:
        """Perform Chi-square test for categorical features."""
        # Get frequency distributions
        ref_counts = self.reference_data[feature].value_counts()
        curr_counts = current_data[feature].value_counts()

        # Align indices
        all_categories = set(ref_counts.index) | set(curr_counts.index)
        ref_freq = np.array([ref_counts.get(cat, 0) for cat in all_categories])
        curr_freq = np.array([curr_counts.get(cat, 0) for cat in all_categories])

        # Normalize to same total
        ref_freq = ref_freq / ref_freq.sum() * curr_freq.sum()

        # Chi-square test
        statistic, p_value = stats.chisquare(curr_freq, ref_freq)

        drift_detected = p_value < self.threshold

        return DriftResult(
            feature=feature,
            drift_detected=drift_detected,
            test_statistic=statistic,
            p_value=p_value,
            drift_score=statistic,
            method='chi_square',
            threshold=self.threshold
        )

    def calculate_psi(self, feature: str, current_data: pd.DataFrame, bins: int = 10) -> DriftResult:
        """
        Calculate Population Stability Index (PSI).

        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Moderate change
        PSI >= 0.2: Significant change
        """
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()

        # Create bins based on reference data
        _, bin_edges = np.histogram(ref_values, bins=bins)

        # Calculate frequencies in each bin
        ref_freq = np.histogram(ref_values, bins=bin_edges)[0] / len(ref_values)
        curr_freq = np.histogram(curr_values, bins=bin_edges)[0] / len(curr_values)

        # Add small constant to avoid log(0)
        ref_freq = np.where(ref_freq == 0, 0.0001, ref_freq)
        curr_freq = np.where(curr_freq == 0, 0.0001, curr_freq)

        # Calculate PSI
        psi = np.sum((curr_freq - ref_freq) * np.log(curr_freq / ref_freq))

        # PSI thresholds
        if psi < 0.1:
            drift_detected = False
        elif psi < 0.2:
            drift_detected = True  # Moderate drift
        else:
            drift_detected = True  # Significant drift

        return DriftResult(
            feature=feature,
            drift_detected=drift_detected,
            test_statistic=psi,
            p_value=1.0 - min(psi / 0.2, 1.0),  # Pseudo p-value
            drift_score=psi,
            method='psi',
            threshold=0.1
        )

    def jensen_shannon_divergence(self, feature: str, current_data: pd.DataFrame, bins: int = 10) -> DriftResult:
        """Calculate Jensen-Shannon divergence between distributions."""
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()

        # Create bins
        _, bin_edges = np.histogram(ref_values, bins=bins)

        # Calculate probability distributions
        ref_prob = np.histogram(ref_values, bins=bin_edges)[0] / len(ref_values)
        curr_prob = np.histogram(curr_values, bins=bin_edges)[0] / len(curr_values)

        # Add small constant
        ref_prob = np.where(ref_prob == 0, 1e-10, ref_prob)
        curr_prob = np.where(curr_prob == 0, 1e-10, curr_prob)

        # Normalize
        ref_prob = ref_prob / ref_prob.sum()
        curr_prob = curr_prob / curr_prob.sum()

        # Calculate JSD
        m = 0.5 * (ref_prob + curr_prob)
        jsd = 0.5 * stats.entropy(ref_prob, m) + 0.5 * stats.entropy(curr_prob, m)

        # JSD is between 0 and 1
        drift_detected = jsd > 0.1

        return DriftResult(
            feature=feature,
            drift_detected=drift_detected,
            test_statistic=jsd,
            p_value=1.0 - jsd,
            drift_score=jsd,
            method='jsd',
            threshold=0.1
        )

    def detect_drift(
        self,
        current_data: pd.DataFrame,
        methods: Optional[List[str]] = None
    ) -> Dict[str, List[DriftResult]]:
        """
        Detect drift across all features using specified methods.

        Args:
            current_data: Current production data to compare against reference
            methods: List of methods to use ['ks_test', 'psi', 'jsd', 'chi_square']
                    If None, uses appropriate method per feature type

        Returns:
            Dictionary mapping feature names to list of drift results
        """
        if methods is None:
            methods = ['ks_test', 'psi']

        results = {}

        for feature in self.feature_columns:
            feature_results = []

            if feature in self.categorical_features:
                # Use chi-square for categorical
                if 'chi_square' in methods:
                    feature_results.append(self.chi_square_test(feature, current_data))
            else:
                # Use multiple methods for continuous features
                if 'ks_test' in methods:
                    feature_results.append(self.ks_test(feature, current_data))
                if 'psi' in methods:
                    feature_results.append(self.calculate_psi(feature, current_data))
                if 'jsd' in methods:
                    feature_results.append(self.jensen_shannon_divergence(feature, current_data))

            results[feature] = feature_results

        return results

    def get_drift_report(self, current_data: pd.DataFrame) -> Dict:
        """Generate comprehensive drift report."""
        drift_results = self.detect_drift(current_data)

        # Analyze results
        drifted_features = []
        total_features = len(self.feature_columns)

        for feature, results in drift_results.items():
            # Feature is drifted if any method detects drift
            if any(r.drift_detected for r in results):
                drifted_features.append(feature)

        drift_percentage = (len(drifted_features) / total_features) * 100

        # Create detailed report
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_features': total_features,
                'drifted_features': len(drifted_features),
                'drift_percentage': drift_percentage,
                'drift_detected': len(drifted_features) > 0
            },
            'drifted_features': drifted_features,
            'detailed_results': {}
        }

        # Add detailed results for drifted features
        for feature in drifted_features:
            report['detailed_results'][feature] = [
                {
                    'method': r.method,
                    'drift_detected': r.drift_detected,
                    'drift_score': r.drift_score,
                    'p_value': r.p_value,
                    'test_statistic': r.test_statistic
                }
                for r in drift_results[feature]
            ]

        return report

    def plot_drift_summary(self, current_data: pd.DataFrame) -> str:
        """Generate text-based drift summary visualization."""
        report = self.get_drift_report(current_data)

        output = []
        output.append("=" * 70)
        output.append("DRIFT DETECTION REPORT")
        output.append("=" * 70)
        output.append(f"Timestamp: {report['timestamp']}")
        output.append(f"Total Features: {report['summary']['total_features']}")
        output.append(f"Drifted Features: {report['summary']['drifted_features']}")
        output.append(f"Drift Percentage: {report['summary']['drift_percentage']:.2f}%")
        output.append("")

        if report['summary']['drift_detected']:
            output.append("⚠️  DRIFT DETECTED")
            output.append("")
            output.append("Drifted Features:")
            for feature in report['drifted_features']:
                output.append(f"  - {feature}")
                for result in report['detailed_results'][feature]:
                    output.append(f"      {result['method']}: score={result['drift_score']:.4f}, p={result['p_value']:.4f}")
        else:
            output.append("✅ NO DRIFT DETECTED")

        output.append("=" * 70)

        return "\n".join(output)


# Example usage
if __name__ == '__main__':
    from pathlib import Path

    # Load sample data
    data_dir = Path(__file__).parent.parent / 'data' / 'samples'

    train_df = pd.read_parquet(data_dir / 'classification_train.parquet')
    drifted_df = pd.read_parquet(data_dir / 'classification_drifted.parquet')

    # Initialize detector with training data as baseline
    detector = DriftDetector(train_df, threshold=0.05)

    # Detect drift on drifted dataset
    print("Testing drift detection on artificially drifted dataset...")
    print(detector.plot_drift_summary(drifted_df))

    # Get detailed report
    report = detector.get_drift_report(drifted_df)

    print(f"\nDrift detected in {report['summary']['drift_percentage']:.1f}% of features")
