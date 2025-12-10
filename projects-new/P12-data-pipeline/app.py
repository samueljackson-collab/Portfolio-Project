from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

ARTIFACT = Path("artifacts/airflow_dag_run.log")
ARTIFACT.parent.mkdir(exist_ok=True)


def extract() -> str:
    return "extracted_sales_2025_01.csv"


def transform(dataset: str) -> str:
    return f"clean_{dataset.replace('.csv', '.parquet')}"


def load(dataset: str) -> str:
    return f"loaded:{dataset}"


def run_dag() -> list[str]:
    steps = []
    steps.append(f"[{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}] Starting DAG run")
    raw = extract()
    steps.append(f"extract -> {raw}")
    cleaned = transform(raw)
    steps.append(f"transform -> {cleaned}")
    loaded = load(cleaned)
    steps.append(f"load -> {loaded}")
    steps.append("DAG completed successfully")
    return steps


def main():
    steps = run_dag()
    ARTIFACT.write_text("\n".join(steps))
    print("Airflow DAG simulation complete. See artifacts/airflow_dag_run.log")


if __name__ == "__main__":
    main()
