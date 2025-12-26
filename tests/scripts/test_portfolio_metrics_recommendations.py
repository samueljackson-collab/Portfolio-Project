"""Tests for recommendation generation in portfolio-metrics script."""
from importlib import util
from pathlib import Path


MODULE_PATH = Path(__file__).parent.parent.parent / "scripts" / "portfolio-metrics.py"


def load_portfolio_metrics():
    """Dynamically load the portfolio-metrics module."""
    spec = util.spec_from_file_location("portfolio_metrics", MODULE_PATH)
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generate_recommendations_renders_commit_total():
    """Ensure commit totals are interpolated into recommendations."""
    module = load_portfolio_metrics()
    metrics = module.PortfolioMetrics(base_dir=Path("."))
    metrics.metrics["github"]["total_commits"] = 42

    recommendations = metrics._generate_recommendations()

    assert recommendations, "Recommendations should not be empty"
    assert "42 total commits" in recommendations[0]
    assert "{metrics.total_commits}" not in recommendations[0]
