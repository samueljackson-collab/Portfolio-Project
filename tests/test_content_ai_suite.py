"""Unit tests for the content SEO helpers."""

from __future__ import annotations

import pytest

from content_seo.core import ContentAISuite


@pytest.mark.parametrize(
    "keywords, sections, expected_headings",
    [
        ([], 3, ["Section 1", "Section 2", "Section 3"]),
        (["primary keyword"], 3, ["Primary Keyword", "Section 2", "Section 3"]),
    ],
)
def test_generate_seo_content_handles_short_keyword_lists(
    keywords: list[str],
    sections: int,
    expected_headings: list[str],
) -> None:
    """Ensure the SEO outline renders even with sparse keyword inputs."""

    suite = ContentAISuite()

    result = suite.generate_seo_content(
        title="Test",
        target_keywords=keywords,
        body_sections=sections,
    )

    outline = result["outline"]

    assert len(outline) == sections
    actual_headings = [section.heading for section in outline]
    assert actual_headings == expected_headings
