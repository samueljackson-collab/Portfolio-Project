from src.advertising.core import AdCreativeAI


def test_ad_creative_handles_string_benefit():
    generator = AdCreativeAI()

    creatives = generator.generate(
        {
            "name": "Artisan Rope",
            "benefits": "durable craftsmanship",
        },
        variations=1,
    )

    assert creatives[0]["headline"].endswith("durable craftsmanship")
    assert "durable craftsmanship" in creatives[0]["primary_text"]
