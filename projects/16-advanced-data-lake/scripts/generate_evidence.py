"""Generate ingestion outputs, catalog metadata, and performance evidence."""
from __future__ import annotations

import json
import shutil
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"
SRC_DIR = PROJECT_ROOT

sys.path.append(str(SRC_DIR))

from src.bronze_to_silver import transform as bronze_to_silver_transform  # noqa: E402
from src.silver_to_gold import AggregationConfig, SilverToGoldTransformer  # noqa: E402


@dataclass
class DatasetMetadata:
    dataset: str
    layer: str
    path: str
    record_count: int
    columns: List[str]
    dtypes: Dict[str, str]
    file_size_bytes: int
    captured_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    (EVIDENCE_DIR / "silver").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "gold").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "tmp").mkdir(parents=True, exist_ok=True)


def run_ingestion() -> Tuple[Dict[str, Path], pd.DataFrame, pd.DataFrame]:
    bronze_path = DATA_DIR / "bronze.json"
    temp_dir = EVIDENCE_DIR / "tmp"
    silver_parquet = temp_dir / "silver.parquet"
    gold_dir = temp_dir / "gold"
    silver_csv = EVIDENCE_DIR / "silver" / "silver.csv"
    gold_csv = EVIDENCE_DIR / "gold" / "gold_data.csv"

    bronze_to_silver_transform(str(bronze_path), str(silver_parquet))

    transformer = SilverToGoldTransformer(AggregationConfig(time_granularity="daily"))
    transformer.transform(str(silver_parquet), str(gold_dir))

    silver_df = pd.read_parquet(silver_parquet)
    gold_df = pd.read_parquet(gold_dir / "gold_data.parquet")

    silver_df.to_csv(silver_csv, index=False)
    gold_df.to_csv(gold_csv, index=False)

    shutil.rmtree(temp_dir)

    return (
        {
            "bronze": bronze_path,
            "silver": silver_csv,
            "gold": gold_csv,
        },
        silver_df,
        gold_df,
    )


def read_json_lines(path: Path) -> pd.DataFrame:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return pd.DataFrame(records)


def build_metadata(paths: Dict[str, Path]) -> List[DatasetMetadata]:
    metadata = []

    for layer, path in paths.items():
        if path.suffix == ".json":
            df = read_json_lines(path)
        else:
            df = pd.read_csv(path)

        metadata.append(
            DatasetMetadata(
                dataset=f"{layer}_layer",
                layer=layer,
                path=str(path.relative_to(PROJECT_ROOT)),
                record_count=len(df),
                columns=list(df.columns),
                dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
                file_size_bytes=path.stat().st_size,
                captured_at=utc_now(),
            )
        )

    return metadata


def save_metadata(metadata: List[DatasetMetadata]) -> Path:
    output_path = EVIDENCE_DIR / "dataset_metadata.json"
    payload = [asdict(entry) for entry in metadata]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def build_schema_catalog(metadata: List[DatasetMetadata]) -> pd.DataFrame:
    rows = []
    for entry in metadata:
        for col_name in entry.columns:
            rows.append(
                {
                    "dataset": entry.dataset,
                    "column": col_name,
                    "dtype": entry.dtypes.get(col_name, ""),
                }
            )
    return pd.DataFrame(rows)


def render_table_image(df: pd.DataFrame, output_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 0.4 * len(df) + 1))
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)
    ax.set_title(title, fontsize=14, pad=12)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def time_query(query_fn: Callable[[], pd.DataFrame], runs: int = 8) -> List[float]:
    durations = []
    for _ in range(runs):
        start = perf_counter()
        query_fn()
        durations.append((perf_counter() - start) * 1000)
    return durations


def capture_query_metrics(silver_df: pd.DataFrame, gold_df: pd.DataFrame) -> pd.DataFrame:
    queries = {
        "silver_filter_success": lambda: silver_df[silver_df["status"] == "success"],
        "silver_group_status": lambda: silver_df.groupby("status").size(),
        "gold_time_bucket": lambda: gold_df.groupby("_time_bucket").size(),
    }

    rows = []
    for name, query in queries.items():
        for run_id, duration_ms in enumerate(time_query(query), start=1):
            rows.append({"query": name, "run": run_id, "duration_ms": duration_ms})

    return pd.DataFrame(rows)


def summarize_query_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for query, group in metrics.groupby("query"):
        durations = group["duration_ms"].tolist()
        summary_rows.append(
            {
                "query": query,
                "avg_ms": statistics.mean(durations),
                "p95_ms": statistics.quantiles(durations, n=20)[-1],
                "runs": len(durations),
            }
        )
    return pd.DataFrame(summary_rows)


def render_latency_chart(summary: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    positions = range(len(summary["query"]))
    ax.bar(positions, summary["avg_ms"], color="#4C78A8")
    ax.set_ylabel("Average latency (ms)")
    ax.set_title("Query Latency (Average)")
    ax.set_xticks(list(positions))
    ax.set_xticklabels(summary["query"], rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_storage_chart(storage_df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(storage_df["layer"], storage_df["size_mb"], marker="o", color="#59A14F")
    ax.set_ylabel("Size (MB)")
    ax.set_title("Storage Growth Across Layers")
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    paths, silver_df, gold_df = run_ingestion()

    metadata = build_metadata(paths)
    save_metadata(metadata)

    schema_df = build_schema_catalog(metadata)
    render_table_image(schema_df, EVIDENCE_DIR / "schema_catalog.svg", "Schema Catalog")

    query_metrics = capture_query_metrics(silver_df, gold_df)
    query_metrics_path = EVIDENCE_DIR / "query_latency_runs.csv"
    query_metrics.to_csv(query_metrics_path, index=False)

    summary_df = summarize_query_metrics(query_metrics)
    summary_path = EVIDENCE_DIR / "query_latency_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    render_latency_chart(summary_df, EVIDENCE_DIR / "query_latency_chart.svg")

    storage_rows = []
    for entry in metadata:
        storage_rows.append(
            {
                "layer": entry.layer,
                "size_mb": round(entry.file_size_bytes / (1024 * 1024), 4),
                "path": entry.path,
            }
        )
    storage_df = pd.DataFrame(storage_rows)
    storage_path = EVIDENCE_DIR / "storage_growth.csv"
    storage_df.to_csv(storage_path, index=False)
    render_storage_chart(storage_df, EVIDENCE_DIR / "storage_growth_chart.svg")

    summary_note = EVIDENCE_DIR / "RUN_SUMMARY.md"
    summary_note.write_text(
        "\n".join(
            [
                "# Evidence Run Summary",
                "",
                f"Run completed: {utc_now()}",
                "",
                "Artifacts:",
                "- dataset_metadata.json",
                "- schema_catalog.svg",
                "- query_latency_runs.csv",
                "- query_latency_summary.csv",
                "- query_latency_chart.svg",
                "- storage_growth.csv",
                "- storage_growth_chart.svg",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
