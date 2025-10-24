"""Content generation helpers for SEO-focused article outlines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence


def _sanitize_keywords(focus_keywords: Optional[Iterable[str]]) -> List[str]:
    """Return a normalized list of keywords with whitespace trimmed.

    Empty or ``None`` entries are filtered out to keep the outline concise.
    """

    if not focus_keywords:
        return []

    normalized: List[str] = []
    for keyword in focus_keywords:
        if keyword is None:
            continue
        cleaned = keyword.strip()
        if cleaned:
            normalized.append(cleaned)
    return normalized


@dataclass(frozen=True)
class OutlineSection:
    """Structured representation of an outline section."""

    order: int
    heading: str
    focus_keyword: Optional[str] = None


@dataclass
class OnPageAnalyzer:
    """Analyse inputs and generate an SEO-aligned outline."""

    fallback_heading_prefix: str = "Section"

    def plan_outline(
        self,
        body_sections: int,
        focus_keywords: Sequence[str] | None,
    ) -> List[OutlineSection]:
        """Generate outline sections for the requested body paragraphs.

        The original implementation assumed that ``focus_keywords`` would always
        be at least as long as ``body_sections``. When this assumption fails the
        lookup ``focus_keywords[index]`` raises an ``IndexError``. To support use
        cases where fewer (or zero) keywords are available, the method now
        guards the lookup and provides a descriptive fallback heading whenever a
        keyword is missing.
        """

        if body_sections < 0:
            raise ValueError("body_sections must be non-negative")

        keywords = _sanitize_keywords(focus_keywords)
        outline: List[OutlineSection] = []

        for index in range(body_sections):
            keyword = keywords[index] if index < len(keywords) else None
            heading = self._build_heading(index + 1, keyword)
            outline.append(
                OutlineSection(
                    order=index + 1,
                    heading=heading,
                    focus_keyword=keyword,
                )
            )

        return outline

    def _build_heading(self, order: int, keyword: Optional[str]) -> str:
        """Create a human readable heading for the outline section."""

        if keyword:
            # Title-case for readability while keeping core keyword phrasing.
            return keyword.title()
        return f"{self.fallback_heading_prefix} {order}"


@dataclass
class ContentAISuite:
    """Facade for building SEO content artefacts."""

    analyzer: OnPageAnalyzer = field(default_factory=OnPageAnalyzer)

    def generate_seo_content(
        self,
        *,
        title: str,
        target_keywords: Sequence[str] | None,
        body_sections: int,
    ) -> dict:
        """Create an SEO outline using the configured :class:`OnPageAnalyzer`.

        Parameters
        ----------
        title:
            Title used for the content artefact. Currently returned verbatim for
            consumers that need to display it alongside the generated outline.
        target_keywords:
            Optional sequence of target keywords supplied by the user.
        body_sections:
            Total number of body sections requested for the outline.
        """

        outline = self.analyzer.plan_outline(
            body_sections=body_sections,
            focus_keywords=target_keywords,
        )

        return {
            "title": title,
            "outline": outline,
            "section_count": len(outline),
        }
