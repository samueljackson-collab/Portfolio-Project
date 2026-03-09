"""Silver to Gold layer transformation with aggregations and business metrics."""
from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

LOGGER = logging.getLogger(__name__)


@dataclass
class AggregationConfig:
    """Configuration for gold layer aggregations."""
    time_granularity: str = "daily"  # hourly, daily, weekly, monthly
    dimensions: List[str] = None
    metrics: Dict[str, str] = None  # metric_name: aggregation_function

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = ["event_type", "status"]
        if self.metrics is None:
            self.metrics = {
                "event_count": "count",
                "unique_users": "nunique",
                "avg_duration": "mean",
                "total_value": "sum",
            }


class SilverToGoldTransformer:
    """Transforms silver layer data to gold layer with aggregations."""

    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self._aggregation_funcs = {
            "count": "count",
            "sum": "sum",
            "mean": "mean",
            "median": "median",
            "min": "min",
            "max": "max",
            "std": "std",
            "nunique": "nunique",
            "first": "first",
            "last": "last",
        }

    def transform(
        self,
        input_path: str,
        output_path: str,
        partition_cols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute silver to gold transformation."""
        start_time = datetime.utcnow()
        LOGGER.info(f"Starting silver-to-gold transformation: {input_path}")

        # Read silver data
        df = pd.read_parquet(input_path)
        initial_rows = len(df)

        # Add time-based grouping column
        df = self._add_time_grouping(df)

        # Build aggregation groups
        group_cols = self._get_group_columns(df)

        # Perform aggregations
        gold_df = self._aggregate(df, group_cols)

        # Calculate derived metrics
        gold_df = self._calculate_derived_metrics(gold_df)

        # Add metadata
        gold_df["_gold_processed_at"] = datetime.utcnow()
        gold_df["_source_row_count"] = initial_rows

        # Write to gold layer
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        if partition_cols:
            self._write_partitioned(gold_df, output_dir, partition_cols)
        else:
            gold_df.to_parquet(output_dir / "gold_data.parquet", index=False)

        duration = (datetime.utcnow() - start_time).total_seconds()
        LOGGER.info(f"Gold transformation complete: {len(gold_df)} rows in {duration:.2f}s")

        return {
            "input_rows": initial_rows,
            "output_rows": len(gold_df),
            "duration_seconds": duration,
            "dimensions": group_cols,
            "metrics": list(self.config.metrics.keys()),
        }

    def _add_time_grouping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based grouping column based on granularity."""
        time_col = self._find_time_column(df)
        if time_col is None:
            LOGGER.warning("No timestamp column found, skipping time grouping")
            return df

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])

        granularity_map = {
            "hourly": "H",
            "daily": "D",
            "weekly": "W",
            "monthly": "M",
        }

        freq = granularity_map.get(self.config.time_granularity, "D")
        df["_time_bucket"] = df[time_col].dt.to_period(freq).dt.to_timestamp()

        return df

    def _find_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the primary timestamp column."""
        time_cols = ["ingested_at", "created_at", "timestamp", "event_time", "date"]
        for col in time_cols:
            if col in df.columns:
                return col
        return None

    def _get_group_columns(self, df: pd.DataFrame) -> List[str]:
        """Get columns to group by."""
        group_cols = []

        if "_time_bucket" in df.columns:
            group_cols.append("_time_bucket")

        for dim in self.config.dimensions:
            if dim in df.columns:
                group_cols.append(dim)

        return group_cols

    def _aggregate(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """Perform aggregations on the dataframe."""
        if not group_cols:
            LOGGER.warning("No group columns, returning summary aggregation")
            return self._summarize(df)

        agg_dict = {}

        # Build aggregation dictionary
        for metric_name, agg_func in self.config.metrics.items():
            source_col = self._find_source_column(df, metric_name, agg_func)
            if source_col:
                if source_col not in agg_dict:
                    agg_dict[source_col] = []
                agg_dict[source_col].append((metric_name, agg_func))

        # Perform grouped aggregation
        if agg_dict:
            agg_spec = {}
            rename_map = {}

            for col, metrics in agg_dict.items():
                for metric_name, agg_func in metrics:
                    agg_key = f"{col}_{agg_func}"
                    agg_spec[agg_key] = pd.NamedAgg(column=col, aggfunc=agg_func)
                    rename_map[agg_key] = metric_name

            result = df.groupby(group_cols, as_index=False).agg(**agg_spec)
            result = result.rename(columns=rename_map)
        else:
            result = df.groupby(group_cols, as_index=False).size()
            result = result.rename(columns={"size": "event_count"})

        return result

    def _find_source_column(self, df: pd.DataFrame, metric_name: str, agg_func: str) -> Optional[str]:
        """Find source column for a metric."""
        # Map metric names to likely source columns
        column_hints = {
            "event_count": "event_id",
            "unique_users": "user_id",
            "avg_duration": "duration",
            "total_value": "value",
        }

        hint = column_hints.get(metric_name)
        if hint and hint in df.columns:
            return hint

        # For count aggregations, use any column
        if agg_func == "count":
            return df.columns[0]

        return None

    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived business metrics."""
        df = df.copy()

        # Calculate rates and ratios if applicable columns exist
        if "event_count" in df.columns and "unique_users" in df.columns:
            df["events_per_user"] = df["event_count"] / df["unique_users"].replace(0, 1)

        if "success_count" in df.columns and "event_count" in df.columns:
            df["success_rate"] = df["success_count"] / df["event_count"].replace(0, 1)

        return df

    def _summarize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a summary aggregation when no group columns."""
        summary = {
            "total_rows": len(df),
            "processed_at": datetime.utcnow(),
        }

        for col in df.select_dtypes(include=["number"]).columns[:5]:
            summary[f"{col}_sum"] = df[col].sum()
            summary[f"{col}_mean"] = df[col].mean()

        return pd.DataFrame([summary])

    def _write_partitioned(
        self,
        df: pd.DataFrame,
        output_dir: Path,
        partition_cols: List[str],
    ) -> None:
        """Write partitioned parquet files."""
        table = pa.Table.from_pandas(df)
        pq.write_to_dataset(
            table,
            root_path=str(output_dir),
            partition_cols=partition_cols,
        )


def main():
    parser = argparse.ArgumentParser(description="Silver to Gold transformation")
    parser.add_argument("--input", required=True, help="Input silver parquet path")
    parser.add_argument("--output", required=True, help="Output gold directory")
    parser.add_argument("--granularity", default="daily", choices=["hourly", "daily", "weekly", "monthly"])
    parser.add_argument("--partition-by", nargs="*", help="Columns to partition by")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config = AggregationConfig(time_granularity=args.granularity)
    transformer = SilverToGoldTransformer(config)

    result = transformer.transform(
        args.input,
        args.output,
        partition_cols=args.partition_by,
    )

    print(f"Transformation complete: {result}")


if __name__ == "__main__":
    main()
