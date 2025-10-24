"""Simulate bronze -> silver Delta transformation using pandas."""
from __future__ import annotations

import argparse
import json
import pandas as pd


def transform(input_path: str, output_path: str) -> None:
    records = [json.loads(line) for line in open(input_path, "r", encoding="utf-8")]
    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["event_id"]).fillna({"status": "unknown"})
    df["ingested_at"] = pd.to_datetime(df["ingested_at"])
    df.to_parquet(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    transform(args.input, args.output)
