"""Prompt assembly helpers for PRJ-AIML-002."""

from __future__ import annotations

import json
from dataclasses import dataclass
from string import Template
from typing import Iterable, Mapping


@dataclass(frozen=True)
class PromptTemplate:
    """Declarative representation of a prompt template."""

    name: str
    body: str
    description: str | None = None

    @classmethod
    def from_json(cls, path: str) -> "PromptTemplate":
        """Load a template from a JSON document.

        The JSON file should contain ``{"name": str, "body": str, "description": str?}``.
        """

        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return cls(
            name=payload["name"],
            body=payload["body"],
            description=payload.get("description"),
        )


def render_prompt(template: PromptTemplate, data: Mapping[str, object]) -> str:
    """Render ``template`` with ``data`` using ``string.Template`` substitution."""

    return Template(template.body).safe_substitute({key: str(value) for key, value in data.items()})


def render_batch(template: PromptTemplate, rows: Iterable[Mapping[str, object]]) -> Iterable[str]:
    """Render prompts for each row in ``rows``.

    Returns a generator of strings to minimise memory usage for large jobs.
    """

    for row in rows:
        yield render_prompt(template, row)
