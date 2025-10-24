"""Portfolio reporting toolkit with multi-format output and analytics."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

__all__ = [
    "AdvancedAIAnalytics",
    "AdvancedReportGenerator",
    "AdvancedVisualizations",
    "ReportScheduler",
]

logger = logging.getLogger(__name__)


class ReportDependencyError(RuntimeError):
    """Raised when an optional dependency required for report generation is missing."""


@dataclass
class ProjectMetrics:
    """Normalized metrics for a single portfolio project."""

    name: str
    completion_percentage: float
    deployment_frequency: float = 0.0
    security_score: float = 0.0
    code_quality: float = 0.0
    performance_score: float = 0.0
    cost_efficiency: float = 0.0
    lead_time: Optional[float] = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ProjectMetrics":
        """Create an instance from a generic mapping, applying sensible defaults."""

        return cls(
            name=str(data.get("name", "Unnamed Project")),
            completion_percentage=float(data.get("completion_percentage", 0.0)),
            deployment_frequency=float(data.get("deployment_frequency", 0.0)),
            security_score=float(data.get("security_score", 0.0)),
            code_quality=float(data.get("code_quality", 0.0)),
            performance_score=float(data.get("performance_score", 0.0)),
            cost_efficiency=float(data.get("cost_efficiency", 0.0)),
            lead_time=(
                float(data["lead_time"]) if data.get("lead_time") is not None else None
            ),
            metadata=dict(data.get("metadata", {})),
        )

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON serialisable representation."""

        payload = {
            "name": self.name,
            "completion_percentage": round(self.completion_percentage, 2),
            "deployment_frequency": round(self.deployment_frequency, 2),
            "security_score": round(self.security_score, 2),
            "code_quality": round(self.code_quality, 2),
            "performance_score": round(self.performance_score, 2),
            "cost_efficiency": round(self.cost_efficiency, 2),
        }
        if self.lead_time is not None:
            payload["lead_time"] = round(self.lead_time, 2)
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


class AdvancedAIAnalytics:
    """Perform predictive analysis and identify delivery bottlenecks."""

    async def predict_completion_timelines(
        self, projects_metrics: Sequence[Mapping[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Predict completion timelines from current progress and velocity."""

        predictions: Dict[str, Dict[str, Any]] = {}
        for project in projects_metrics:
            metrics = ProjectMetrics.from_mapping(project)
            velocity = self.calculate_velocity(project)
            current_completion = max(0.0, min(metrics.completion_percentage, 100.0))
            if velocity > 0:
                remaining = 100.0 - current_completion
                predicted_weeks = remaining / velocity
                predictions[metrics.name] = {
                    "predicted_completion_date": (
                        datetime.utcnow() + timedelta(weeks=predicted_weeks)
                    ).isoformat(),
                    "confidence": min(95.0, current_completion + 20.0),
                    "weekly_velocity": round(velocity, 2),
                }
            else:
                predictions[metrics.name] = {
                    "predicted_completion_date": None,
                    "confidence": max(5.0, current_completion / 2.0),
                    "weekly_velocity": 0.0,
                }
        return predictions

    async def identify_bottlenecks(
        self, projects_metrics: Sequence[Mapping[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify likely delivery or quality bottlenecks for projects."""

        bottlenecks: List[Dict[str, Any]] = []
        for project in projects_metrics:
            metrics = ProjectMetrics.from_mapping(project)
            if metrics.completion_percentage < 50.0 and metrics.deployment_frequency < 5:
                bottlenecks.append(
                    {
                        "project": metrics.name,
                        "type": "development_velocity",
                        "severity": "high",
                        "recommendation": (
                            "Increase deployment frequency and code review efficiency"
                        ),
                    }
                )
            if metrics.security_score < 80.0:
                bottlenecks.append(
                    {
                        "project": metrics.name,
                        "type": "security_vulnerabilities",
                        "severity": "critical" if metrics.security_score < 60 else "high",
                        "recommendation": "Conduct security audit and implement fixes",
                    }
                )
            if metrics.code_quality < 75.0:
                bottlenecks.append(
                    {
                        "project": metrics.name,
                        "type": "code_quality",
                        "severity": "medium",
                        "recommendation": "Expand automated testing and peer reviews",
                    }
                )
        return bottlenecks

    def calculate_velocity(self, project: Mapping[str, Any]) -> float:
        """Estimate weekly completion velocity for a project."""

        if "velocity" in project:
            try:
                return max(0.0, float(project["velocity"]))
            except (TypeError, ValueError):
                return 0.0

        history = project.get("history")
        if isinstance(history, Iterable):
            deltas: List[float] = []
            previous = None
            for point in history:
                completion = point.get("completion_percentage") if isinstance(point, Mapping) else None
                if completion is None:
                    continue
                completion = float(completion)
                if previous is not None:
                    deltas.append(max(0.0, completion - previous))
                previous = completion
            if deltas:
                return sum(deltas) / len(deltas)

        weeks_tracked = project.get("weeks_tracked") or project.get("duration_weeks")
        if weeks_tracked:
            try:
                return max(0.0, float(project.get("completion_percentage", 0.0)) / float(weeks_tracked))
            except (TypeError, ValueError, ZeroDivisionError):
                return 0.0
        return 0.0


class AdvancedVisualizations:
    """Create Plotly-based interactive assets for the reports."""

    def __init__(self, output_dir: Path | str = Path("reports")) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def create_portfolio_health_radar(self, portfolio_metrics: Mapping[str, Any]) -> Optional[Path]:
        """Generate a radar chart illustrating the overall portfolio health."""

        try:
            import plotly.graph_objects as go
        except ImportError as exc:  # pragma: no cover - optional dependency
            logger.debug("Plotly unavailable for radar chart: %s", exc)
            raise ReportDependencyError("plotly is required for radar charts") from exc

        categories = [
            "Completion",
            "Code Quality",
            "Security",
            "Performance",
            "Cost Efficiency",
        ]
        overall = portfolio_metrics.get("overall", {})
        values = [
            float(overall.get("portfolio_health_score", 0.0)),
            float(overall.get("code_quality", 0.0)),
            float(overall.get("security_score", 0.0)),
            float(overall.get("performance_score", 0.0)),
            float(overall.get("cost_efficiency", 0.0)),
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(r=values, theta=categories, fill="toself", name="Portfolio Health")
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="Portfolio Health Radar Chart",
            template="plotly_white",
        )

        output_path = self.output_dir / "health_radar.html"
        await asyncio.to_thread(fig.write_html, str(output_path))
        return output_path

    async def create_trend_analysis(self, historical_metrics: Sequence[Mapping[str, Any]]) -> Optional[Path]:
        """Generate a trend chart showing how metrics evolve over time."""

        try:
            import pandas as pd
            import plotly.express as px
        except ImportError as exc:  # pragma: no cover - optional dependency
            logger.debug("Plotly/Pandas unavailable for trend analysis: %s", exc)
            raise ReportDependencyError("pandas and plotly are required for trend analysis") from exc

        if not historical_metrics:
            return None

        df = pd.DataFrame(historical_metrics)
        if "date" not in df.columns:
            df["date"] = pd.date_range(start=datetime.utcnow() - timedelta(weeks=len(df)), periods=len(df), freq="W")
        df.sort_values("date", inplace=True)

        metrics_to_chart = [
            column
            for column in df.columns
            if column != "date" and df[column].dtype != "O"
        ]
        if not metrics_to_chart:
            return None

        fig = px.line(df, x="date", y=metrics_to_chart, markers=True, title="Portfolio Metrics Trend Analysis")
        fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Score")

        output_path = self.output_dir / "trend_analysis.html"
        await asyncio.to_thread(fig.write_html, str(output_path))
        return output_path


class AdvancedReportGenerator:
    """Produce comprehensive portfolio reports across multiple formats."""

    def __init__(
        self,
        output_dir: Path | str = Path("reports"),
        metrics_loader: Optional[Callable[[], Mapping[str, Any]]] = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_loader = metrics_loader or self._default_metrics
        self.analytics = AdvancedAIAnalytics()
        self.visualizations = AdvancedVisualizations(self.output_dir)

    async def generate_portfolio_report(
        self,
        report_type: str,
        output_formats: Optional[Sequence[str]] = None,
        metrics: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Path]:
        """Generate a portfolio report in the requested output formats."""

        resolved_metrics = metrics or self.metrics_loader()
        context = await self._build_context(report_type, resolved_metrics)
        formats = [fmt.lower() for fmt in (output_formats or ("pdf", "html", "markdown", "json", "excel"))]

        handlers = {
            "markdown": self._generate_markdown,
            "html": self._generate_html,
            "json": self._generate_json,
            "pdf": self._generate_pdf,
            "excel": self._generate_excel,
        }

        outputs: Dict[str, Path] = {}
        for fmt in formats:
            handler = handlers.get(fmt)
            if not handler:
                raise ValueError(f"Unsupported report format: {fmt}")
            try:
                result = await handler(context, resolved_metrics)
            except ReportDependencyError as exc:
                logger.warning("Skipping %s report due to missing dependency: %s", fmt, exc)
                continue
            if result is not None:
                outputs[fmt] = result
        return outputs

    async def _build_context(
        self, report_type: str, metrics: Mapping[str, Any]
    ) -> Dict[str, Any]:
        projects = [ProjectMetrics.from_mapping(entry).as_dict() for entry in metrics.get("projects", [])]
        predictions, bottlenecks = await asyncio.gather(
            self.analytics.predict_completion_timelines(metrics.get("projects", [])),
            self.analytics.identify_bottlenecks(metrics.get("projects", [])),
        )

        visuals: Dict[str, Optional[Path]] = {}
        try:
            visuals["health_radar"] = await self.visualizations.create_portfolio_health_radar(metrics)
        except ReportDependencyError as exc:
            logger.warning("Unable to build radar chart: %s", exc)
            visuals["health_radar"] = None
        try:
            visuals["trend_analysis"] = await self.visualizations.create_trend_analysis(
                metrics.get("historical", [])
            )
        except ReportDependencyError as exc:
            logger.warning("Unable to build trend analysis chart: %s", exc)
            visuals["trend_analysis"] = None

        generated_at = datetime.utcnow()
        slug = f"{report_type.replace(' ', '_').lower()}_{generated_at.strftime('%Y%m%d%H%M%S')}"
        summary = self._summarise_projects(projects)

        return {
            "report_type": report_type,
            "generated_at": generated_at,
            "slug": slug,
            "projects": projects,
            "overall": metrics.get("overall", {}),
            "historical": metrics.get("historical", []),
            "predictions": predictions,
            "bottlenecks": bottlenecks,
            "visuals": visuals,
            "summary": summary,
        }

    def _summarise_projects(self, projects: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not projects:
            return {"project_count": 0, "average_completion": 0.0}
        completion = sum(float(p.get("completion_percentage", 0.0)) for p in projects) / len(projects)
        deployment_frequency = sum(float(p.get("deployment_frequency", 0.0)) for p in projects) / len(projects)
        return {
            "project_count": len(projects),
            "average_completion": round(completion, 2),
            "average_deployment_frequency": round(deployment_frequency, 2),
        }

    async def _generate_markdown(
        self, context: Mapping[str, Any], _: Mapping[str, Any]
    ) -> Path:
        lines = [
            f"# Portfolio Report: {context['report_type']}",
            "",
            f"Generated: {context['generated_at'].isoformat()}",
            "",
            "## Summary",
            f"- Projects tracked: {context['summary']['project_count']}",
            f"- Average completion: {context['summary']['average_completion']}%",
            f"- Average deployment frequency: {context['summary'].get('average_deployment_frequency', 0)} per month",
            "",
        ]

        lines.append("## AI Predictions")
        predictions = context.get("predictions", {})
        if predictions:
            for name, payload in predictions.items():
                lines.append(f"- **{name}**: completion ETA {payload['predicted_completion_date'] or 'unknown'} (confidence {payload['confidence']}%)")
        else:
            lines.append("- No predictions available")
        lines.append("")

        lines.append("## Identified Bottlenecks")
        bottlenecks = context.get("bottlenecks", [])
        if bottlenecks:
            for issue in bottlenecks:
                lines.append(
                    f"- **{issue['project']}** ({issue['type']} – {issue['severity']}): {issue['recommendation']}"
                )
        else:
            lines.append("- No critical bottlenecks detected")
        lines.append("")

        lines.append("## Projects")
        for project in context.get("projects", []):
            lines.extend(
                [
                    f"### {project['name']}",
                    f"- Completion: {project['completion_percentage']}%",
                    f"- Deployments/month: {project['deployment_frequency']}",
                    f"- Code quality: {project['code_quality']}",
                    f"- Security score: {project['security_score']}",
                    f"- Performance score: {project['performance_score']}",
                    f"- Cost efficiency: {project['cost_efficiency']}",
                    "",
                ]
            )

        markdown_content = "\n".join(lines)
        output_path = self.output_dir / f"{context['slug']}.md"
        await asyncio.to_thread(output_path.write_text, markdown_content, encoding="utf-8")
        return output_path

    async def _generate_html(self, context: Mapping[str, Any], _: Mapping[str, Any]) -> Path:
        try:
            from jinja2 import Environment, BaseLoader, select_autoescape
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ReportDependencyError("jinja2 is required for HTML reports") from exc

        template = Environment(
            loader=BaseLoader(), autoescape=select_autoescape(["html", "xml"])
        ).from_string(
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Portfolio Report - {{ report_type }}</title>
    <style>
        body { font-family: system-ui, sans-serif; margin: 2rem; color: #1f2933; }
        h1 { color: #1f2937; }
        h2 { border-bottom: 1px solid #d1d5db; padding-bottom: .25rem; }
        .project { margin-bottom: 1.5rem; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
        .metric-card { background: #f3f4f6; padding: 0.75rem; border-radius: 0.5rem; }
        .bottleneck { background: #fee2e2; border-left: 4px solid #ef4444; padding: 0.75rem; margin-bottom: 0.75rem; }
        .predictions { background: #ecfeff; border-left: 4px solid #06b6d4; padding: 0.75rem; margin-bottom: 0.75rem; }
        footer { margin-top: 2rem; font-size: 0.875rem; color: #6b7280; }
    </style>
</head>
<body>
    <h1>Portfolio Report: {{ report_type }}</h1>
    <p>Generated {{ generated_at.isoformat() }}</p>

    <section>
        <h2>Summary</h2>
        <div class="metrics">
            <div class="metric-card">
                <strong>Projects Tracked</strong>
                <div>{{ summary.project_count }}</div>
            </div>
            <div class="metric-card">
                <strong>Average Completion</strong>
                <div>{{ summary.average_completion }}%</div>
            </div>
            <div class="metric-card">
                <strong>Deployments / Month</strong>
                <div>{{ summary.average_deployment_frequency }}</div>
            </div>
        </div>
    </section>

    <section>
        <h2>AI Predictions</h2>
        {% if predictions %}
            {% for name, payload in predictions.items() %}
            <div class="predictions">
                <strong>{{ name }}</strong><br />
                ETA: {{ payload.predicted_completion_date or 'unknown' }}<br />
                Confidence: {{ payload.confidence }}%
            </div>
            {% endfor %}
        {% else %}
            <p>No predictions available.</p>
        {% endif %}
    </section>

    <section>
        <h2>Bottlenecks</h2>
        {% if bottlenecks %}
            {% for issue in bottlenecks %}
            <div class="bottleneck">
                <strong>{{ issue.project }}</strong> ({{ issue.type }} – {{ issue.severity }})<br />
                {{ issue.recommendation }}
            </div>
            {% endfor %}
        {% else %}
            <p>No critical bottlenecks detected.</p>
        {% endif %}
    </section>

    <section>
        <h2>Projects</h2>
        {% for project in projects %}
        <div class="project">
            <h3>{{ project.name }}</h3>
            <div class="metrics">
                <div class="metric-card">Completion: {{ project.completion_percentage }}%</div>
                <div class="metric-card">Deployments / Month: {{ project.deployment_frequency }}</div>
                <div class="metric-card">Code Quality: {{ project.code_quality }}</div>
                <div class="metric-card">Security Score: {{ project.security_score }}</div>
                <div class="metric-card">Performance: {{ project.performance_score }}</div>
                <div class="metric-card">Cost Efficiency: {{ project.cost_efficiency }}</div>
            </div>
        </div>
        {% endfor %}
    </section>

    <section>
        <h2>Visual Assets</h2>
        <ul>
            {% if visuals.health_radar %}
            <li><a href="{{ visuals.health_radar.name }}">Portfolio health radar</a></li>
            {% endif %}
            {% if visuals.trend_analysis %}
            <li><a href="{{ visuals.trend_analysis.name }}">Trend analysis dashboard</a></li>
            {% endif %}
        </ul>
    </section>

    <footer>Generated by the Advanced Report Generator.</footer>
</body>
</html>
            """
        )

        html_content = template.render(**context)
        output_path = self.output_dir / f"{context['slug']}.html"
        await asyncio.to_thread(output_path.write_text, html_content, encoding="utf-8")
        return output_path

    async def _generate_json(self, context: Mapping[str, Any], _: Mapping[str, Any]) -> Path:
        payload = {
            "report_type": context["report_type"],
            "generated_at": context["generated_at"].isoformat(),
            "projects": context.get("projects", []),
            "summary": context.get("summary", {}),
            "predictions": context.get("predictions", {}),
            "bottlenecks": context.get("bottlenecks", []),
        }
        output_path = self.output_dir / f"{context['slug']}.json"
        await asyncio.to_thread(
            lambda: output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        )
        return output_path

    async def _generate_pdf(self, context: Mapping[str, Any], _: Mapping[str, Any]) -> Path:
        try:
            from fpdf import FPDF
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ReportDependencyError("fpdf2 is required for PDF reports") from exc

        markdown_path = await self._generate_markdown(context, {})
        text = await asyncio.to_thread(markdown_path.read_text, encoding="utf-8")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in text.splitlines():
            pdf.multi_cell(0, 8, line)
        output_path = self.output_dir / f"{context['slug']}.pdf"
        await asyncio.to_thread(pdf.output, str(output_path))
        return output_path

    async def _generate_excel(self, context: Mapping[str, Any], _: Mapping[str, Any]) -> Path:
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ReportDependencyError("pandas is required for Excel reports") from exc

        projects_df = pd.DataFrame(context.get("projects", []))
        summary_df = pd.DataFrame(
            [
                {"Metric": "Projects", "Value": context["summary"]["project_count"]},
                {
                    "Metric": "Average Completion",
                    "Value": context["summary"]["average_completion"],
                },
                {
                    "Metric": "Deployments / Month",
                    "Value": context["summary"].get("average_deployment_frequency", 0.0),
                },
            ]
        )
        predictions = context.get("predictions", {})
        predictions_df = pd.DataFrame(
            [
                {
                    "Project": name,
                    "ETA": payload.get("predicted_completion_date"),
                    "Confidence": payload.get("confidence"),
                    "Velocity": payload.get("weekly_velocity"),
                }
                for name, payload in predictions.items()
            ]
        )

        output_path = self.output_dir / f"{context['slug']}.xlsx"

        def write_excel() -> None:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                projects_df.to_excel(writer, sheet_name="Projects", index=False)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                if not predictions_df.empty:
                    predictions_df.to_excel(writer, sheet_name="AI Predictions", index=False)

        await asyncio.to_thread(write_excel)
        return output_path

    def _default_metrics(self) -> Dict[str, Any]:
        generated = datetime.utcnow()
        projects = [
            {
                "name": "AWS Infrastructure Automation",
                "completion_percentage": 95.0,
                "deployment_frequency": 12,
                "security_score": 93,
                "code_quality": 91,
                "performance_score": 90,
                "cost_efficiency": 88,
                "history": [
                    {"week": 1, "completion_percentage": 40},
                    {"week": 4, "completion_percentage": 72},
                    {"week": 8, "completion_percentage": 95},
                ],
            },
            {
                "name": "Advanced Cybersecurity Platform",
                "completion_percentage": 88.0,
                "deployment_frequency": 8,
                "security_score": 97,
                "code_quality": 89,
                "performance_score": 87,
                "cost_efficiency": 82,
                "history": [
                    {"week": 1, "completion_percentage": 30},
                    {"week": 4, "completion_percentage": 55},
                    {"week": 8, "completion_percentage": 78},
                    {"week": 12, "completion_percentage": 88},
                ],
            },
            {
                "name": "Observability & Incident Response",
                "completion_percentage": 92.0,
                "deployment_frequency": 10,
                "security_score": 88,
                "code_quality": 90,
                "performance_score": 91,
                "cost_efficiency": 86,
                "history": [
                    {"week": 1, "completion_percentage": 45},
                    {"week": 4, "completion_percentage": 70},
                    {"week": 8, "completion_percentage": 85},
                    {"week": 10, "completion_percentage": 92},
                ],
            },
        ]

        historical = [
            {
                "date": generated - timedelta(weeks=idx),
                "portfolio_health_score": 70 + idx * 1.2,
                "code_quality": 82 + idx * 0.8,
                "security_score": 85 + idx * 0.6,
            }
            for idx in range(12)
        ]

        return {
            "overall": {
                "portfolio_health_score": 90,
                "code_quality": 92,
                "security_score": 94,
                "performance_score": 89,
                "cost_efficiency": 85,
            },
            "projects": projects,
            "historical": list(reversed(historical)),
        }


class ReportScheduler:
    """Schedule background report generation jobs."""

    def __init__(self, generator_factory: Optional[Any] = None) -> None:
        self.generator_factory = generator_factory or AdvancedReportGenerator
        self.schedules: List[Dict[str, Any]] = []

    def add_schedule(self, schedule: Mapping[str, Any]) -> None:
        self.schedules.append(dict(schedule))

    async def run_scheduled_report(self, schedule: Mapping[str, Any]) -> None:
        while True:
            now = datetime.utcnow()
            if self.should_run_report(schedule, now):
                logger.info("Running scheduled report: %s", schedule.get("report_type"))
                generator = self.generator_factory()
                try:
                    await generator.generate_portfolio_report(
                        report_type=schedule.get("report_type", "scheduled"),
                        output_formats=schedule.get("formats", ("pdf", "html")),
                    )
                    logger.info("Scheduled report completed: %s", schedule.get("report_type"))
                except Exception as exc:  # pragma: no cover - defensive
                    logger.error("Scheduled report failed: %s", exc)
            await asyncio.sleep(3600)

    def should_run_report(self, schedule: Mapping[str, Any], current_time: datetime) -> bool:
        frequency = schedule.get("frequency", "daily").lower()
        scheduled_time = str(schedule.get("time", "00:00"))
        try:
            target_hour = int(scheduled_time.split(":")[0])
        except (ValueError, AttributeError):
            target_hour = 0

        if frequency == "daily":
            return current_time.hour == target_hour
        if frequency == "weekly":
            day = str(schedule.get("day", "monday")).lower()
            return current_time.strftime("%A").lower() == day and current_time.hour == target_hour
        if frequency == "monthly":
            try:
                day_of_month = int(schedule.get("day", 1))
            except (TypeError, ValueError):
                day_of_month = 1
            return current_time.day == day_of_month and current_time.hour == target_hour
        return False
