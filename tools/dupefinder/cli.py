"""Command line interface for the duplicate finder service."""

from __future__ import annotations

from pathlib import Path
import typer

from .service import DupeFinderService

app = typer.Typer(help="Media duplicate finder utilities")


def _service(db: Path) -> DupeFinderService:
    database_url = f"sqlite:///{db}" if db != Path(":memory:") else "sqlite:///:memory:"
    return DupeFinderService(database_url=database_url)


@app.command()
def index(
    path: Path = typer.Argument(..., exists=True, file_okay=False, readable=True),
    db: Path = typer.Option(Path("dupefinder.db"), "--db", help="SQLite database location."),
) -> None:
    """Index all media files within ``path``."""

    service = _service(db.resolve())
    count = service.index_path(path.resolve())
    typer.echo(f"Indexed {count} files from {path}")


@app.command()
def match(
    threshold: float = typer.Option(0.85, min=0.0, max=1.0, help="Similarity threshold."),
    db: Path = typer.Option(Path("dupefinder.db"), "--db", help="SQLite database location."),
) -> None:
    """Find potential duplicates and print them to stdout."""

    service = _service(db.resolve())
    results = service.match(threshold=threshold)
    if not results:
        typer.echo("No potential duplicates found.")
        raise typer.Exit(code=0)
    for group in results:
        typer.echo(f"{group.score:.2f}\t{group.reason}\t{', '.join(group.paths)}")


def main() -> None:
    """Entry point allowing invocation from ``python -m``."""

    app(standalone_mode=True, prog_name="dupefinder")


if __name__ == "__main__":  # pragma: no cover
    main()
