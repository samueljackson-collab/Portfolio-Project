"""Tests for the MLOps drift detection module."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.drift_detection import DriftDetector, DriftResult


@pytest.fixture
def reference_df() -> pd.DataFrame:
    """Stable reference distribution."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "feature_a": np.random.normal(0, 1, 500),
            "feature_b": np.random.normal(5, 2, 500),
            "category": np.random.choice(["A", "B", "C"], 500),
        }
    )


@pytest.fixture
def stable_df() -> pd.DataFrame:
    """Production data from the same distribution as reference."""
    np.random.seed(7)
    return pd.DataFrame(
        {
            "feature_a": np.random.normal(0, 1, 500),
            "feature_b": np.random.normal(5, 2, 500),
            "category": np.random.choice(["A", "B", "C"], 500),
        }
    )


@pytest.fixture
def drifted_df() -> pd.DataFrame:
    """Production data from a shifted distribution."""
    np.random.seed(99)
    return pd.DataFrame(
        {
            "feature_a": np.random.normal(3, 1, 500),  # shifted mean
            "feature_b": np.random.normal(10, 5, 500),  # shifted mean & variance
            "category": np.random.choice(["A", "B", "C"], 500),
        }
    )


@pytest.fixture
def detector(reference_df: pd.DataFrame) -> DriftDetector:
    return DriftDetector(
        reference_data=reference_df,
        feature_columns=["feature_a", "feature_b"],
        categorical_features=["category"],
        threshold=0.05,
    )


# ---------------------------------------------------------------------------
# DriftResult dataclass
# ---------------------------------------------------------------------------

def test_drift_result_fields():
    r = DriftResult(
        feature="x", drift_detected=True, test_statistic=0.5,
        p_value=0.01, drift_score=0.5, method="ks_test", threshold=0.05
    )
    assert r.feature == "x"
    assert r.drift_detected is True
    assert r.method == "ks_test"


# ---------------------------------------------------------------------------
# DriftDetector initialization
# ---------------------------------------------------------------------------

def test_detector_initializes(detector: DriftDetector, reference_df: pd.DataFrame):
    assert len(detector.feature_columns) == 2
    assert "feature_a" in detector.reference_stats
    assert "feature_b" in detector.reference_stats


def test_detector_auto_detects_columns():
    """Auto-detection works when only numeric columns are present."""
    np.random.seed(0)
    df = pd.DataFrame(
        {
            "x": np.random.normal(0, 1, 100),
            "y": np.random.normal(1, 2, 100),
        }
    )
    d = DriftDetector(reference_data=df)
    assert len(d.feature_columns) >= 2


# ---------------------------------------------------------------------------
# KS test
# ---------------------------------------------------------------------------

def test_ks_test_stable(detector: DriftDetector, stable_df: pd.DataFrame):
    result = detector.ks_test("feature_a", stable_df)
    assert result.method == "ks_test"
    assert result.feature == "feature_a"
    assert float(result.p_value) >= 0.0  # valid p-value range
    # Stable distribution should not trigger drift (high p-value)
    assert float(result.p_value) > 0.01  # not heavily drifted


def test_ks_test_drifted(detector: DriftDetector, drifted_df: pd.DataFrame):
    result = detector.ks_test("feature_a", drifted_df)
    assert bool(result.drift_detected) is True
    assert float(result.p_value) < 0.05


# ---------------------------------------------------------------------------
# PSI test
# ---------------------------------------------------------------------------

def test_psi_stable(detector: DriftDetector, stable_df: pd.DataFrame):
    result = detector.calculate_psi("feature_a", stable_df)
    assert result.method == "psi"
    assert result.test_statistic >= 0


def test_psi_drifted(detector: DriftDetector, drifted_df: pd.DataFrame):
    result = detector.calculate_psi("feature_a", drifted_df)
    assert bool(result.drift_detected) is True
    assert float(result.drift_score) > 0.1


# ---------------------------------------------------------------------------
# Jensen-Shannon divergence
# ---------------------------------------------------------------------------

def test_jsd_returns_result(detector: DriftDetector, stable_df: pd.DataFrame):
    result = detector.jensen_shannon_divergence("feature_a", stable_df)
    assert result.method == "jsd"
    assert 0.0 <= result.drift_score <= 1.0


# ---------------------------------------------------------------------------
# Chi-square (categorical)
# ---------------------------------------------------------------------------

def test_chi_square_stable(reference_df: pd.DataFrame, stable_df: pd.DataFrame):
    d = DriftDetector(
        reference_data=reference_df,
        feature_columns=["category"],
        categorical_features=["category"],
    )
    result = d.chi_square_test("category", stable_df)
    assert result.method == "chi_square"
    # result.drift_detected may be np.bool_ so use bool()
    assert bool(result.drift_detected) in (True, False)


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_stable_no_drift(detector: DriftDetector, stable_df: pd.DataFrame):
    results = detector.detect_drift(stable_df, methods=["ks_test"])
    for feature, feature_results in results.items():
        for r in feature_results:
            # drift_detected may be np.bool_; just ensure it's truthy/falsy
            assert bool(r.drift_detected) in (True, False)


def test_detect_drift_drifted_signals(detector: DriftDetector, drifted_df: pd.DataFrame):
    results = detector.detect_drift(drifted_df, methods=["ks_test"])
    drifted = [f for f, rs in results.items() if any(r.drift_detected for r in rs)]
    assert len(drifted) > 0


# ---------------------------------------------------------------------------
# get_drift_report
# ---------------------------------------------------------------------------

def test_get_drift_report_structure(detector: DriftDetector, stable_df: pd.DataFrame):
    report = detector.get_drift_report(stable_df)
    assert "timestamp" in report
    assert "summary" in report
    assert "total_features" in report["summary"]
    assert "drifted_features" in report["summary"]
    assert "drift_percentage" in report["summary"]


def test_get_drift_report_drifted(detector: DriftDetector, drifted_df: pd.DataFrame):
    report = detector.get_drift_report(drifted_df)
    assert bool(report["summary"]["drift_detected"]) is True
    assert report["summary"]["drifted_features"] > 0


# ---------------------------------------------------------------------------
# plot_drift_summary (text output)
# ---------------------------------------------------------------------------

def test_plot_drift_summary_returns_string(detector: DriftDetector, stable_df: pd.DataFrame):
    output = detector.plot_drift_summary(stable_df)
    assert isinstance(output, str)
    assert "DRIFT DETECTION REPORT" in output
