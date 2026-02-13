from pathlib import Path

from typer.testing import CliRunner

from tools.dupefinder.cli import app
from tools.dupefinder.service import DupeFinderService


def _write_file(path: Path, content: bytes) -> None:
    path.write_bytes(content)


def test_service_index_and_match(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    _write_file(media_dir / "photo1.jpg", b"duplicate content")
    _write_file(media_dir / "photo2.jpg", b"duplicate content")
    _write_file(media_dir / "unique.png", b"unique content")

    db_path = tmp_path / "dupes.sqlite"
    service = DupeFinderService(database_url=f"sqlite:///{db_path}")
    indexed = service.index_path(media_dir)
    assert indexed == 3

    matches = service.match(threshold=0.85)
    assert matches, "Expected at least one duplicate suggestion"
    assert any(len(result.paths) >= 2 for result in matches)


def test_cli_integration(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    _write_file(media_dir / "song1.mp3", b"audio sample")
    _write_file(media_dir / "song1_copy.mp3", b"audio sample")

    db = tmp_path / "cli.sqlite"
    runner = CliRunner()
    result_index = runner.invoke(app, ["index", str(media_dir), "--db", str(db)])
    assert result_index.exit_code == 0
    assert "Indexed 2 files" in result_index.stdout

    result_match = runner.invoke(app, ["match", "--db", str(db), "--threshold", "0.8"])
    assert result_match.exit_code == 0
    assert "song1.mp3" in result_match.stdout
    assert "song1_copy.mp3" in result_match.stdout
