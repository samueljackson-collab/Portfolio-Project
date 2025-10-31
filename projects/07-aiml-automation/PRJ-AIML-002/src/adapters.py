"""Data adapter utilities for PRJ-AIML-002.

The helpers here intentionally depend only on the Python standard library so
that the automation toolkit can run in lightweight execution environments (e.g.
GitHub Actions, ephemeral containers).  They cover the minimum viable feature
set required by the developer workflow documented in this project.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence


@dataclass(frozen=True)
class DatasetSpec:
    """Describe where a dataset lives and how it should be parsed."""

    path: Path
    kind: str | None = None
    encoding: str = "utf-8"

    def detect_kind(self) -> str:
        """Infer the dataset type from the file extension when not provided."""

        if self.kind:
            return self.kind
        suffix = self.path.suffix.lower()
        if suffix in {".csv", ".tsv"}:
            return "delimited"
        if suffix in {".json"}:
            return "json"
        raise ValueError(f"Unsupported dataset type for {self.path!s}")


def load_records(spec: DatasetSpec) -> List[Mapping[str, str]]:
    """Load tabular records from CSV/TSV/JSON documents.

    Returns a list of dictionaries ready to be consumed by prompt builders or
    templating engines.  JSON payloads are expected to be arrays of objects.
    """

    kind = spec.detect_kind()
    if kind == "delimited":
        delimiter = ","
        if spec.path.suffix.lower() == ".tsv":
            delimiter = "\t"
        with spec.path.open("r", encoding=spec.encoding, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            return [row for row in reader]
    if kind == "json":
        with spec.path.open("r", encoding=spec.encoding) as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError("JSON payload must be an array of objects")
        return [ensure_string_map(item) for item in data]
    raise ValueError(f"Unsupported dataset kind: {kind}")


def ensure_string_map(item: Mapping[str, object]) -> Mapping[str, str]:
    """Convert mapping values to strings for downstream templating."""

    return {key: str(value) for key, value in item.items()}


def chunk_records(records: Sequence[Mapping[str, str]], *, chunk_size: int) -> Iterable[Sequence[Mapping[str, str]]]:
    """Yield the input records in fixed-size chunks.

    Used by the prompt orchestration code when large datasets need to be broken
    into manageable batches before dispatching work to an LLM endpoint.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    batch: List[Mapping[str, str]] = []
    for record in records:
        batch.append(record)
        if len(batch) == chunk_size:
            yield tuple(batch)
            batch.clear()
    if batch:
        yield tuple(batch)
