from __future__ import annotations

import os
from pathlib import Path

from tools.dupefinder.service import DuplicateFinderService
from tools.dupefinder import models


def setup_module(module):
    if models.DB_PATH.exists():
        os.remove(models.DB_PATH)
    models.Base.metadata.create_all(models.engine)


def test_index_and_match(tmp_path: Path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("hello world", encoding="utf-8")
    file_b.write_text("hello world", encoding="utf-8")

    service = DuplicateFinderService()
    count = service.index_path(tmp_path)
    assert count == 2

    results = service.find_matches(threshold=0.8)
    assert results
    all_files = {entry["media"] for entry in results}
    assert str(file_a) in all_files or str(file_b) in all_files
