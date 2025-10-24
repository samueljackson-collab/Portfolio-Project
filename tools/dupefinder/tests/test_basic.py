from __future__ import annotations
from pathlib import Path

from typer.testing import CliRunner

from tools.dupefinder import DupeFinderService
from tools.dupefinder import cli


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf8")


def test_service_detects_duplicates(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    file_a = data_dir / "clip_a.txt"
    file_b = data_dir / "clip_b.txt"
    file_c = data_dir / "clip_c.txt"

    payload = "hello world"
    _write(file_a, payload)
    _write(file_b, payload)
    _write(file_c, "another payload")

    service = DupeFinderService()
    indexed = service.index_path(data_dir)
    assert indexed == 3

    matches = service.match(threshold=0.8)
    assert matches, "Expected at least one duplicate pair"

    pair_paths = {(Path(item["a"]).name, Path(item["b"]).name) for item in matches}
    assert (file_a.name, file_b.name) in pair_paths or (file_b.name, file_a.name) in pair_paths
    assert all(0.0 <= item["score"] <= 1.0 for item in matches)


def test_cli_index_and_match(tmp_path):
    data_dir = tmp_path / "cli"
    data_dir.mkdir()
    duplicate_a = data_dir / "dup1.txt"
    duplicate_b = data_dir / "dup2.txt"
    _write(duplicate_a, "duplicate content")
    _write(duplicate_b, "duplicate content")

    database = tmp_path / "cli.sqlite"

    runner = CliRunner()
    result = runner.invoke(cli.app, ["index", str(data_dir), "--database", str(database)])
    assert result.exit_code == 0, result.output
    assert "Indexed" in result.output

    result = runner.invoke(
        cli.app,
        ["match", "--database", str(database), "--threshold", "0.8"],
    )
    assert result.exit_code == 0, result.output
    assert "<->" in result.output
