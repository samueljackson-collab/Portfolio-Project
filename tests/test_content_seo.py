import asyncio

from src.content_seo.core import ContentAISuite


def test_generate_content_with_sparse_keywords():
    suite = ContentAISuite()

    result = asyncio.run(
        suite.generate_seo_content(
            topic="Rope Craft",
            target_keywords=[],
            tone="informative",
            word_count=600,
        )
    )

    outline = result["outline"]
    assert len(outline) >= 5
    assert all("heading" in section and section["heading"] for section in outline)
    assert all("keyword_focus" in section for section in outline)
