"""Integration tests for the migration orchestrator using a live Postgres service."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest

try:
    import psycopg2
except ModuleNotFoundError:  # pragma: no cover - handled by pytest skip
    psycopg2 = None

PROJECT_SRC = Path(__file__).resolve().parents[2] / "projects" / "2-database-migration" / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

pytest.importorskip("psycopg2")

from migration_orchestrator import DatabaseConfig, DatabaseMigrationOrchestrator  # noqa: E402


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        pytest.skip(f"Environment variable {var_name} is not set")
    return value


@pytest.fixture(scope="module")
def postgres_env() -> Dict[str, str]:
    """Return connection information for the CI-managed Postgres container."""
    host = _require_env("POSTGRES_HOST")
    port = _require_env("POSTGRES_PORT")
    user = _require_env("POSTGRES_USER")
    password = _require_env("POSTGRES_PASSWORD")
    source_db = os.getenv("POSTGRES_SOURCE_DB", "migration_source")
    target_db = os.getenv("POSTGRES_TARGET_DB", "migration_target")
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "source_db": source_db,
        "target_db": target_db,
    }


def _wait_for_postgres(conn_info: Dict[str, str]) -> None:
    deadline = time.time() + 60
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                dbname="postgres",
                user=conn_info["user"],
                password=conn_info["password"],
            )
            conn.close()
            return
        except psycopg2.OperationalError as exc:  # pragma: no cover - best effort polling
            last_error = exc
            time.sleep(2)
    if last_error:
        raise last_error


def _ensure_database(conn_info: Dict[str, str], db_name: str) -> None:
    conn = psycopg2.connect(
        host=conn_info["host"],
        port=conn_info["port"],
        dbname="postgres",
        user=conn_info["user"],
        password=conn_info["password"],
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
    conn.close()


@pytest.mark.integration
@patch("migration_orchestrator.boto3")
def test_validate_connectivity_against_live_postgres(mock_boto3: MagicMock, postgres_env: Dict[str, str]):
    """Validate that the orchestrator can connect to the provisioned Postgres databases."""
    _wait_for_postgres(postgres_env)
    _ensure_database(postgres_env, postgres_env["source_db"])
    _ensure_database(postgres_env, postgres_env["target_db"])

    mock_boto3.client.return_value = MagicMock()

    source_config = DatabaseConfig(
        host=postgres_env["host"],
        port=int(postgres_env["port"]),
        database=postgres_env["source_db"],
        username=postgres_env["user"],
        password=postgres_env["password"],
        ssl_mode="disable",
    )
    target_config = DatabaseConfig(
        host=postgres_env["host"],
        port=int(postgres_env["port"]),
        database=postgres_env["target_db"],
        username=postgres_env["user"],
        password=postgres_env["password"],
        ssl_mode="disable",
    )

    orchestrator = DatabaseMigrationOrchestrator(
        source_config=source_config,
        target_config=target_config,
        max_replication_lag_seconds=5,
    )

    assert orchestrator.validate_connectivity() is True
