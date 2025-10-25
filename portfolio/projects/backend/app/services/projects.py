from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from app.models import Project


@lru_cache
def _load_seed_data() -> tuple[Project, ...]:
    """Load projects from the repository seed file."""
    resolved = Path(__file__).resolve()
    candidates = []

    if len(resolved.parents) >= 5:
        candidates.append(resolved.parents[4] / "data" / "seed_projects.json")

    candidates.append(resolved.parents[1] / "data" / "seed_projects.json")

    for seed_path in candidates:
        if seed_path.exists():
            break
    else:  # pragma: no cover - defensive branch
        msg = "Seed data file not found in expected locations."
        raise FileNotFoundError(msg)

    with seed_path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    return tuple(Project.model_validate(item) for item in payload)


def list_projects() -> Iterable[Project]:
    return _load_seed_data()
