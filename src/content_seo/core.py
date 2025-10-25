"""Utilities for generating simple SEO-friendly filler content.

This module intentionally keeps the logic lightweight so the unit tests can
exercise the behaviour around keyword cycling without depending on an external
API or heavyweight data model.
"""
from __future__ import annotations

from itertools import cycle
from typing import Iterable, Iterator

DEFAULT_FALLBACK_KEYWORDS: tuple[str, ...] = ("general insights",)
"""Default keyword(s) used when research fails to provide any options.

The tuple form makes it easy to extend in the future while still supporting the
`itertools.cycle` API which expects a finite, indexable data structure.
"""


def _normalise_keywords(keywords: Iterable[str] | None) -> list[str]:
    """Sanitise a keyword collection so it can be safely cycled.

    Parameters
    ----------
    keywords:
        Any iterable of strings (or string-like values). ``None`` is treated the
        same as an empty iterable to simplify callers.

    Returns
    -------
    list[str]
        A list containing all non-empty, trimmed keyword strings.
    """

    if not keywords:
        return []

    normalised: list[str] = []
    for raw_keyword in keywords:
        if raw_keyword is None:
            continue
        keyword = str(raw_keyword).strip()
        if keyword:
            normalised.append(keyword)
    return normalised


def _cycle_keywords(keywords: Iterable[str] | None) -> Iterator[str]:
    """Return an endless iterator over the provided keywords.

    The function is defensive so that a call to :func:`next` never blocks or
    raises :class:`StopIteration` when no meaningful keywords were supplied.
    Instead, it falls back to :data:`DEFAULT_FALLBACK_KEYWORDS` which keeps
    :func:`craft_content` responsive even when research fails to source
    suggestions.
    """

    normalised = _normalise_keywords(keywords)
    if not normalised:
        return cycle(DEFAULT_FALLBACK_KEYWORDS)
    return cycle(normalised)


def _build_paragraph(topic: str, keyword: str) -> str:
    """Create a short paragraph weaving the topic and keyword together."""

    safe_topic = topic.strip() or "This topic"
    return (
        f"{safe_topic} explores {keyword} in practical terms. "
        f"It offers placeholder guidance while deeper research is underway."
    )


def craft_content(
    topic: str,
    keywords: Iterable[str] | None = None,
    paragraphs: int = 2,
) -> str:
    """Generate lightweight filler content around a topic and keyword set.

    Parameters
    ----------
    topic:
        The main subject of the generated content.
    keywords:
        Optional iterable of supporting keywords. An empty iterable is
        acceptable and triggers a sensible fallback.
    paragraphs:
        Number of paragraphs to produce. Must be a positive integer.

    Returns
    -------
    str
        Multi-paragraph content ready to be displayed or inspected by tests.
    """

    if paragraphs < 1:
        raise ValueError("paragraph count must be at least 1")

    keyword_iter = _cycle_keywords(keywords)

    chunks = []
    for _ in range(paragraphs):
        keyword = next(keyword_iter)
        chunks.append(_build_paragraph(topic, keyword))

    return "\n\n".join(chunks)


__all__ = [
    "DEFAULT_FALLBACK_KEYWORDS",
    "craft_content",
]
