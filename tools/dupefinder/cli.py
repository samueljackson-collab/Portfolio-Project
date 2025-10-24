"""Command line interface for the duplicate finder toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .service import DupeFinderService

app = typer.Typer(help="Media duplicate detection utilities.")


def _get_service(database: Optional[str]) -> DupeFinderService:
    return DupeFinderService(db_url=database or "sqlite:///dupefinder.db")


@app.command()
def index(
    path: Path = typer.Argument(..., exists=True, readable=True, file_okay=False),
    database: Optional[str] = typer.Option(
        None, "--database", "-d", help="SQLite database URL or path."
    ),
) -> None:
    """Index the media content found within *path*."""
    service = _get_service(database)
    count = service.index_path(path)
    typer.echo(
        f"Indexed {count} files from {path} into {service.database_url}."
    )


@app.command()
def match(
    threshold: float = typer.Option(0.85, min=0.0, max=1.0, help="Match score threshold"),
    database: Optional[str] = typer.Option(
        None, "--database", "-d", help="SQLite database URL or path."
    ),
) -> None:
    """Find potential duplicates in the existing index."""
    service = _get_service(database)
    matches = service.match(threshold=threshold)
    if not matches:
        typer.echo("No matches found.")
        return
    for pair in matches:
        typer.echo(
            f"{pair['a']} <-> {pair['b']} (score={pair['score']:.3f})"
        )


if __name__ == "__main__":
    app()
