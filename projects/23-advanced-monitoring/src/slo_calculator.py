"""SLO/SLI calculation and error budget tracking."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class SLOType(Enum):
    """Types of SLO measurements."""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class SLODefinition:
    """Defines an SLO target."""
    name: str
    slo_type: SLOType
    target: float  # Target percentage (e.g., 99.9 for 99.9%)
    window_days: int = 30
    description: str = ""
    critical: bool = False

    # For latency SLOs
    latency_threshold_ms: Optional[float] = None
    latency_percentile: float = 95.0


@dataclass
class SLIMetric:
    """Represents a Service Level Indicator measurement."""
    timestamp: datetime
    slo_name: str
    total_events: int
    good_events: int
    bad_events: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_events == 0:
            return 100.0
        return (self.good_events / self.total_events) * 100


@dataclass
class ErrorBudget:
    """Tracks error budget consumption."""
    slo_name: str
    target_percentage: float
    window_days: int
    total_budget_minutes: float
    consumed_minutes: float
    remaining_minutes: float
    burn_rate: float  # How fast budget is being consumed
    projected_exhaustion: Optional[datetime] = None

    @property
    def remaining_percentage(self) -> float:
        if self.total_budget_minutes == 0:
            return 0.0
        return (self.remaining_minutes / self.total_budget_minutes) * 100

    @property
    def is_critical(self) -> bool:
        return self.remaining_percentage < 20.0


@dataclass
class SLOReport:
    """Complete SLO status report."""
    slo: SLODefinition
    current_value: float
    is_meeting_target: bool
    error_budget: ErrorBudget
    trend: str  # "improving", "stable", "degrading"
    measurements: List[SLIMetric] = field(default_factory=list)


class SLOCalculator:
    """Calculates SLO compliance and error budgets."""

    def __init__(self):
        self.slos: Dict[str, SLODefinition] = {}
        self.measurements: Dict[str, List[SLIMetric]] = {}

    def register_slo(self, slo: SLODefinition) -> None:
        """Register an SLO definition."""
        self.slos[slo.name] = slo
        self.measurements[slo.name] = []
        LOGGER.info(f"Registered SLO: {slo.name} (target: {slo.target}%)")

    def record_measurement(self, metric: SLIMetric) -> None:
        """Record an SLI measurement."""
        if metric.slo_name not in self.slos:
            LOGGER.warning(f"Unknown SLO: {metric.slo_name}")
            return

        self.measurements[metric.slo_name].append(metric)

        # Trim old measurements
        slo = self.slos[metric.slo_name]
        cutoff = datetime.utcnow() - timedelta(days=slo.window_days)
        self.measurements[metric.slo_name] = [
            m for m in self.measurements[metric.slo_name]
            if m.timestamp > cutoff
        ]

    def calculate_sli(self, slo_name: str) -> float:
        """Calculate current SLI value."""
        if slo_name not in self.slos:
            return 0.0

        metrics = self.measurements.get(slo_name, [])
        if not metrics:
            return 100.0

        total_events = sum(m.total_events for m in metrics)
        good_events = sum(m.good_events for m in metrics)

        if total_events == 0:
            return 100.0

        return (good_events / total_events) * 100

    def calculate_error_budget(self, slo_name: str) -> ErrorBudget:
        """Calculate error budget for an SLO."""
        if slo_name not in self.slos:
            raise ValueError(f"Unknown SLO: {slo_name}")

        slo = self.slos[slo_name]
        current_sli = self.calculate_sli(slo_name)

        # Calculate total budget in minutes
        window_minutes = slo.window_days * 24 * 60
        allowed_error_rate = 100 - slo.target
        total_budget_minutes = window_minutes * (allowed_error_rate / 100)

        # Calculate consumed budget
        actual_error_rate = 100 - current_sli
        consumed_minutes = window_minutes * (actual_error_rate / 100)

        remaining_minutes = max(0, total_budget_minutes - consumed_minutes)

        # Calculate burn rate (how fast are we consuming budget)
        # Burn rate of 1.0 means we're on track to exactly use budget
        # > 1.0 means we're consuming too fast
        if total_budget_minutes > 0:
            burn_rate = consumed_minutes / total_budget_minutes
        else:
            burn_rate = float('inf') if consumed_minutes > 0 else 0

        # Project when budget will be exhausted
        projected_exhaustion = None
        if burn_rate > 1.0 and remaining_minutes > 0:
            # At current rate, when will we run out?
            days_to_exhaustion = remaining_minutes / (burn_rate * 24 * 60) * slo.window_days
            projected_exhaustion = datetime.utcnow() + timedelta(days=days_to_exhaustion)

        return ErrorBudget(
            slo_name=slo_name,
            target_percentage=slo.target,
            window_days=slo.window_days,
            total_budget_minutes=total_budget_minutes,
            consumed_minutes=consumed_minutes,
            remaining_minutes=remaining_minutes,
            burn_rate=burn_rate,
            projected_exhaustion=projected_exhaustion,
        )

    def generate_report(self, slo_name: str) -> SLOReport:
        """Generate a complete SLO report."""
        if slo_name not in self.slos:
            raise ValueError(f"Unknown SLO: {slo_name}")

        slo = self.slos[slo_name]
        current_value = self.calculate_sli(slo_name)
        error_budget = self.calculate_error_budget(slo_name)

        # Determine trend
        metrics = self.measurements.get(slo_name, [])
        trend = self._calculate_trend(metrics)

        return SLOReport(
            slo=slo,
            current_value=current_value,
            is_meeting_target=current_value >= slo.target,
            error_budget=error_budget,
            trend=trend,
            measurements=metrics[-100:],  # Last 100 measurements
        )

    def _calculate_trend(self, metrics: List[SLIMetric]) -> str:
        """Calculate trend from recent measurements."""
        if len(metrics) < 2:
            return "stable"

        # Compare first half vs second half
        mid = len(metrics) // 2
        first_half = metrics[:mid]
        second_half = metrics[mid:]

        first_avg = sum(m.success_rate for m in first_half) / len(first_half)
        second_avg = sum(m.success_rate for m in second_half) / len(second_half)

        diff = second_avg - first_avg

        if diff > 1.0:
            return "improving"
        elif diff < -1.0:
            return "degrading"
        return "stable"

    def get_all_reports(self) -> List[SLOReport]:
        """Get reports for all registered SLOs."""
        return [self.generate_report(name) for name in self.slos]

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts for SLOs that need attention."""
        alerts = []

        for slo_name in self.slos:
            report = self.generate_report(slo_name)

            if not report.is_meeting_target:
                alerts.append({
                    "severity": "critical" if report.slo.critical else "warning",
                    "slo_name": slo_name,
                    "message": f"SLO {slo_name} is below target: {report.current_value:.2f}% < {report.slo.target}%",
                    "error_budget_remaining": report.error_budget.remaining_percentage,
                })

            if report.error_budget.is_critical:
                alerts.append({
                    "severity": "warning",
                    "slo_name": slo_name,
                    "message": f"Error budget critical: {report.error_budget.remaining_percentage:.1f}% remaining",
                    "projected_exhaustion": report.error_budget.projected_exhaustion,
                })

        return alerts


def create_default_slos() -> SLOCalculator:
    """Create calculator with default portfolio SLOs."""
    calculator = SLOCalculator()

    # Availability SLO
    calculator.register_slo(SLODefinition(
        name="api-availability",
        slo_type=SLOType.AVAILABILITY,
        target=99.9,
        window_days=30,
        description="API should be available 99.9% of the time",
        critical=True,
    ))

    # Latency SLO
    calculator.register_slo(SLODefinition(
        name="api-latency-p95",
        slo_type=SLOType.LATENCY,
        target=95.0,
        window_days=7,
        description="95% of requests should complete within 500ms",
        latency_threshold_ms=500,
        latency_percentile=95.0,
    ))

    # Error rate SLO
    calculator.register_slo(SLODefinition(
        name="error-rate",
        slo_type=SLOType.ERROR_RATE,
        target=99.5,
        window_days=7,
        description="Error rate should be below 0.5%",
    ))

    return calculator
