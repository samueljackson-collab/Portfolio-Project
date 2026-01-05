"""Historical comparison and trend analysis for portfolio reports."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProjectSnapshot:
    """Snapshot of project metrics at a point in time."""

    project_id: str
    timestamp: str
    completion: int
    lines_of_code: int
    files_count: int
    has_tests: bool
    has_ci_cd: bool
    has_docker: bool
    technologies: List[str]
    status: str


@dataclass
class ComparisonResult:
    """Result of comparing two snapshots."""

    metric: str
    previous_value: Any
    current_value: Any
    delta: Any
    delta_percentage: Optional[float]
    trend: str  # "up", "down", "stable"
    interpretation: str


class HistoricalComparison:
    """Compare current portfolio state with historical data."""

    def __init__(self, history_dir: Path):
        """
        Initialize historical comparison.

        Args:
            history_dir: Directory containing historical snapshots
        """
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Historical comparison initialized: {history_dir}")

    def save_snapshot(
        self, snapshot_data: Dict[str, Any], timestamp: Optional[datetime] = None
    ) -> Path:
        """
        Save current portfolio snapshot.

        Args:
            snapshot_data: Current portfolio data
            timestamp: Snapshot timestamp (default: now)

        Returns:
            Path to saved snapshot file
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create filename with timestamp
        filename = f"snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        snapshot_path = self.history_dir / filename

        # Add metadata
        snapshot_data["snapshot_timestamp"] = timestamp.isoformat()
        snapshot_data["snapshot_version"] = "1.0"

        # Save to file
        with open(snapshot_path, "w") as f:
            json.dump(snapshot_data, f, indent=2)

        logger.info(f"Snapshot saved: {snapshot_path}")
        return snapshot_path

    def load_snapshot(self, snapshot_path: Path) -> Dict[str, Any]:
        """
        Load snapshot from file.

        Args:
            snapshot_path: Path to snapshot file

        Returns:
            Snapshot data
        """
        with open(snapshot_path, "r") as f:
            return json.load(f)

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get most recent snapshot.

        Returns:
            Latest snapshot data or None if no snapshots exist
        """
        snapshots = sorted(self.history_dir.glob("snapshot_*.json"), reverse=True)
        if not snapshots:
            logger.warning("No historical snapshots found")
            return None

        return self.load_snapshot(snapshots[0])

    def get_snapshot_before(
        self, reference_date: datetime, days_back: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Get snapshot from approximately N days before reference date.

        Args:
            reference_date: Reference date
            days_back: Number of days to look back

        Returns:
            Snapshot data or None if not found
        """
        target_date = reference_date - timedelta(days=days_back)

        # Find closest snapshot
        snapshots = list(self.history_dir.glob("snapshot_*.json"))
        if not snapshots:
            return None

        closest_snapshot = None
        min_diff = float("inf")

        for snapshot_path in snapshots:
            # Extract date from filename
            try:
                date_str = snapshot_path.stem.replace("snapshot_", "")
                snapshot_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")

                # Calculate difference
                diff = abs((snapshot_date - target_date).total_seconds())

                if diff < min_diff:
                    min_diff = diff
                    closest_snapshot = snapshot_path
            except Exception as e:
                logger.warning(f"Error parsing snapshot filename {snapshot_path}: {e}")

        if closest_snapshot:
            return self.load_snapshot(closest_snapshot)

        return None

    def compare_snapshots(
        self, current: Dict[str, Any], previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two portfolio snapshots.

        Args:
            current: Current snapshot data
            previous: Previous snapshot data

        Returns:
            Comparison results
        """
        logger.info("Comparing snapshots...")

        current_summary = current.get("summary", {})
        previous_summary = previous.get("summary", {})

        comparisons = []

        # Compare key metrics
        metrics = [
            ("total_projects", "Total Projects", False),
            ("avg_completion", "Average Completion %", True),
            ("total_lines", "Total Lines of Code", False),
            ("total_files", "Total Files", False),
            ("projects_with_tests", "Projects with Tests", False),
            ("projects_with_ci_cd", "Projects with CI/CD", False),
            ("projects_with_docker", "Projects with Docker", False),
        ]

        for metric_key, metric_name, is_percentage in metrics:
            prev_val = previous_summary.get(metric_key, 0)
            curr_val = current_summary.get(metric_key, 0)

            comparison = self._compare_metric(
                metric_name, prev_val, curr_val, is_percentage
            )
            comparisons.append(comparison)

        # Compare project statuses
        status_comparison = self._compare_status_breakdown(
            previous_summary.get("status_breakdown", {}),
            current_summary.get("status_breakdown", {}),
        )

        # Compare technology stack
        tech_comparison = self._compare_tech_stack(
            previous_summary.get("tech_stack_count", {}),
            current_summary.get("tech_stack_count", {}),
        )

        # Generate insights
        insights = self._generate_insights(comparisons)

        return {
            "current_timestamp": current.get("snapshot_timestamp"),
            "previous_timestamp": previous.get("snapshot_timestamp"),
            "time_delta_days": self._calculate_time_delta(
                current.get("snapshot_timestamp"), previous.get("snapshot_timestamp")
            ),
            "metric_comparisons": [asdict(c) for c in comparisons],
            "status_comparison": status_comparison,
            "tech_stack_comparison": tech_comparison,
            "insights": insights,
            "summary": self._generate_summary(comparisons),
        }

    def _compare_metric(
        self,
        metric_name: str,
        prev_val: float,
        curr_val: float,
        is_percentage: bool = False,
    ) -> ComparisonResult:
        """Compare a single metric."""
        delta = curr_val - prev_val

        # Calculate percentage change
        if prev_val != 0:
            delta_pct = (delta / prev_val) * 100
        else:
            delta_pct = 100.0 if curr_val > 0 else 0.0

        # Determine trend
        if abs(delta_pct) < 1:
            trend = "stable"
        elif delta > 0:
            trend = "up"
        else:
            trend = "down"

        # Generate interpretation
        if trend == "stable":
            interpretation = "No significant change"
        elif trend == "up":
            interpretation = f"Increased by {abs(delta_pct):.1f}%"
        else:
            interpretation = f"Decreased by {abs(delta_pct):.1f}%"

        return ComparisonResult(
            metric=metric_name,
            previous_value=prev_val,
            current_value=curr_val,
            delta=delta,
            delta_percentage=delta_pct,
            trend=trend,
            interpretation=interpretation,
        )

    def _compare_status_breakdown(
        self, previous: Dict[str, int], current: Dict[str, int]
    ) -> Dict[str, Any]:
        """Compare project status breakdowns."""
        all_statuses = set(previous.keys()) | set(current.keys())

        changes = {}
        for status in all_statuses:
            prev = previous.get(status, 0)
            curr = current.get(status, 0)
            delta = curr - prev

            if delta != 0:
                changes[status] = {"previous": prev, "current": curr, "delta": delta}

        return {"previous": previous, "current": current, "changes": changes}

    def _compare_tech_stack(
        self, previous: Dict[str, int], current: Dict[str, int]
    ) -> Dict[str, Any]:
        """Compare technology stack usage."""
        # Find new technologies
        new_techs = set(current.keys()) - set(previous.keys())

        # Find removed technologies
        removed_techs = set(previous.keys()) - set(current.keys())

        # Find changed usage
        changed = {}
        for tech in set(previous.keys()) & set(current.keys()):
            prev = previous[tech]
            curr = current[tech]
            if prev != curr:
                changed[tech] = {
                    "previous": prev,
                    "current": curr,
                    "delta": curr - prev,
                }

        return {
            "new_technologies": list(new_techs),
            "removed_technologies": list(removed_techs),
            "usage_changes": changed,
            "total_technologies_previous": len(previous),
            "total_technologies_current": len(current),
        }

    def _calculate_time_delta(
        self, current_timestamp: str, previous_timestamp: str
    ) -> float:
        """Calculate days between timestamps."""
        try:
            curr_dt = datetime.fromisoformat(current_timestamp.replace("Z", "+00:00"))
            prev_dt = datetime.fromisoformat(previous_timestamp.replace("Z", "+00:00"))
            delta = curr_dt - prev_dt
            return delta.total_seconds() / 86400  # Convert to days
        except Exception:
            return 0.0

    def _generate_insights(self, comparisons: List[ComparisonResult]) -> List[str]:
        """Generate insights from comparisons."""
        insights = []

        # Check for significant improvements
        for comp in comparisons:
            if (
                comp.trend == "up"
                and comp.delta_percentage
                and comp.delta_percentage > 10
            ):
                insights.append(
                    f"✅ Significant improvement in {comp.metric}: {comp.interpretation}"
                )

        # Check for concerning trends
        for comp in comparisons:
            if (
                comp.trend == "down"
                and comp.delta_percentage
                and comp.delta_percentage < -10
            ):
                insights.append(
                    f"⚠️ Notable decrease in {comp.metric}: {comp.interpretation}"
                )

        # Check for high completion
        completion_comp = next(
            (c for c in comparisons if "Completion" in c.metric), None
        )
        if completion_comp and completion_comp.current_value >= 90:
            insights.append("🎉 Portfolio has reached high completion rate (90%+)")

        if not insights:
            insights.append("Portfolio metrics remain stable")

        return insights

    def _generate_summary(self, comparisons: List[ComparisonResult]) -> str:
        """Generate human-readable summary."""
        up_count = sum(1 for c in comparisons if c.trend == "up")
        down_count = sum(1 for c in comparisons if c.trend == "down")
        stable_count = sum(1 for c in comparisons if c.trend == "stable")

        if up_count > down_count:
            overall = "improving"
        elif down_count > up_count:
            overall = "declining"
        else:
            overall = "stable"

        return (
            f"Overall portfolio trend: {overall}. "
            f"{up_count} metrics improved, {down_count} declined, {stable_count} remained stable."
        )

    def get_trend_data(
        self, metric: str, days: int = 30
    ) -> List[Tuple[datetime, float]]:
        """
        Get trend data for a metric over time.

        Args:
            metric: Metric key to track
            days: Number of days to look back

        Returns:
            List of (timestamp, value) tuples
        """
        cutoff = datetime.now() - timedelta(days=days)
        snapshots = sorted(self.history_dir.glob("snapshot_*.json"))

        trend_data = []

        for snapshot_path in snapshots:
            try:
                # Extract date from filename
                date_str = snapshot_path.stem.replace("snapshot_", "")
                snapshot_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")

                # Skip if too old
                if snapshot_date < cutoff:
                    continue

                # Load and extract metric
                data = self.load_snapshot(snapshot_path)
                value = data.get("summary", {}).get(metric)

                if value is not None:
                    trend_data.append((snapshot_date, value))

            except Exception as e:
                logger.warning(f"Error processing snapshot {snapshot_path}: {e}")

        return sorted(trend_data)


def main():
    """Example usage of historical comparison."""
    import argparse

    parser = argparse.ArgumentParser(description="Historical Comparison Tool")
    parser.add_argument(
        "--history-dir", type=str, default="./history", help="History directory"
    )
    parser.add_argument(
        "--action",
        choices=["save", "compare", "trend"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--data-file", type=str, help="Current data file (for save/compare)"
    )
    parser.add_argument(
        "--days-back", type=int, default=7, help="Days to look back for comparison"
    )
    parser.add_argument("--metric", type=str, help="Metric to track (for trend)")

    args = parser.parse_args()

    history_dir = Path(args.history_dir)
    comparator = HistoricalComparison(history_dir)

    if args.action == "save":
        if not args.data_file:
            print("Error: --data-file required for save action")
            return

        with open(args.data_file, "r") as f:
            current_data = json.load(f)

        snapshot_path = comparator.save_snapshot(current_data)
        print(f"Snapshot saved: {snapshot_path}")

    elif args.action == "compare":
        if not args.data_file:
            print("Error: --data-file required for compare action")
            return

        with open(args.data_file, "r") as f:
            current_data = json.load(f)

        previous_data = comparator.get_snapshot_before(datetime.now(), args.days_back)

        if not previous_data:
            print(f"No snapshot found from {args.days_back} days ago")
            return

        comparison = comparator.compare_snapshots(current_data, previous_data)

        print("\n=== Portfolio Comparison ===\n")
        print(
            f"Comparing: {comparison['previous_timestamp']} → {comparison['current_timestamp']}"
        )
        print(f"Time delta: {comparison['time_delta_days']:.1f} days\n")

        print("Summary:", comparison["summary"])
        print("\nInsights:")
        for insight in comparison["insights"]:
            print(f"  {insight}")

        print("\nMetric Changes:")
        for comp in comparison["metric_comparisons"]:
            trend_icon = (
                "↑"
                if comp["trend"] == "up"
                else "↓" if comp["trend"] == "down" else "→"
            )
            print(
                f"  {trend_icon} {comp['metric']}: {comp['previous_value']} → {comp['current_value']} ({comp['interpretation']})"
            )

    elif args.action == "trend":
        if not args.metric:
            print("Error: --metric required for trend action")
            return

        trend_data = comparator.get_trend_data(args.metric, args.days_back)

        print(f"\n=== Trend Data: {args.metric} (last {args.days_back} days) ===\n")
        for timestamp, value in trend_data:
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M')}: {value}")


if __name__ == "__main__":
    main()
