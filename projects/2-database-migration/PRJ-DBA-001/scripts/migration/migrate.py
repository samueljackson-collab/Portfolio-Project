#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path


def run_psql(sql: str) -> str:
    cmd = ["psql", "-At", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def ensure_migrations_table():
    run_psql(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "id serial PRIMARY KEY,"
        "filename text NOT NULL UNIQUE,"
        "applied_at timestamptz NOT NULL DEFAULT now()"
        ");"
    )


def applied_migrations() -> set[str]:
    output = run_psql("SELECT filename FROM schema_migrations;")
    return set(filter(None, output.splitlines()))


def apply_migration(path: Path):
    print(f"Applying {path.name}")
    result = subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-f", str(path)])
    if result.returncode != 0:
        raise RuntimeError(f"Migration failed: {path.name}")
    run_psql(
        "INSERT INTO schema_migrations (filename) VALUES ('" + path.name + "');"
    )


def main():
    migrations_dir = Path(os.environ.get("MIGRATIONS_DIR", "./scripts/migration/schema_migrations"))
    if not migrations_dir.exists():
        raise SystemExit(f"Migrations directory not found: {migrations_dir}")

    ensure_migrations_table()
    applied = applied_migrations()

    migrations = sorted(p for p in migrations_dir.glob("*.sql") if p.is_file())
    for migration in migrations:
        if migration.name in applied:
            continue
        apply_migration(migration)

    print("Migrations complete")


if __name__ == "__main__":
    main()
