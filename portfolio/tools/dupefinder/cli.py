from __future__ import annotations

import json
from pathlib import Path

import typer

from .service import DuplicateFinderService

app = typer.Typer(help="Media duplicate finder")
service = DuplicateFinderService()


@app.command()
def index(path: Path) -> None:
    """Index media files in PATH."""
    count = service.index_path(path)
    typer.echo(f"Indexed {count} items from {path}")


@app.command()
def match(threshold: float = typer.Option(0.85, help="Match threshold")) -> None:
    """Return potential duplicate matches as JSON."""
    results = service.find_matches(threshold=threshold)
    typer.echo(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    app()
