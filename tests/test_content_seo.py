import pathlib
import sys

# Ensure the ``src`` layout is importable when the project is run directly via
# ``pytest`` without an installed package.
ROOT = pathlib.Path(__file__).resolve().parents[1]
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest

from content_seo.core import DEFAULT_FALLBACK_KEYWORDS, _cycle_keywords, craft_content


def test_cycle_keywords_empty_iterable_returns_fallback_keyword():
    iterator = _cycle_keywords([])

    # ``next`` should immediately return the fallback keyword without blocking
    # or raising ``StopIteration``.
    assert next(iterator) == DEFAULT_FALLBACK_KEYWORDS[0]
    assert next(iterator) == DEFAULT_FALLBACK_KEYWORDS[0]


def test_craft_content_handles_empty_keywords_gracefully():
    topic = "search experience"
    content = craft_content(topic, keywords=[], paragraphs=1)

    assert isinstance(content, str)
    assert DEFAULT_FALLBACK_KEYWORDS[0] in content
    assert topic in content.lower()


def test_craft_content_requires_positive_paragraph_count():
    with pytest.raises(ValueError):
        craft_content("topic", keywords=["one"], paragraphs=0)
