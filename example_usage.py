"""Quick smoke test for the MonkAI local marketing suite primitives."""

import asyncio

from src.advertising.core import AdvertisingAI
from src.content_seo.core import ContentAISuite
from src.video_production.core import VideoAIPipeline


async def main() -> None:
    content_suite = ContentAISuite()
    video_suite = VideoAIPipeline()
    ad_suite = AdvertisingAI()

    print("Generating SEO content...")
    seo_result = await content_suite.generate_seo_content(
        topic="artisan rope making",
        target_keywords=["handmade rope", "climbing rope", "natural fiber rope"],
        tone="professional",
        word_count=800,
    )
    print(f"Generated content preview: {seo_result['content'][:200]}...")

    print("\nCreating video shorts...")
    video_script = (
        "Discover the art of handmade rope making. Traditional techniques meet modern quality."
    )
    video_result = video_suite.create_shorts(script=video_script, style="tiktok")
    print(f"Video created at: {video_result['video_path']}")

    print("\nGenerating ad creatives...")
    product_info = {
        "name": "Artisan Climbing Rope",
        "type": "outdoor equipment",
        "price": 89.99,
        "benefits": ["durable", "lightweight", "eco-friendly"],
    }
    ad_result = ad_suite.generate_ad_creatives(product_info)
    print(f"Generated {len(ad_result['creatives'])} ad variations")


if __name__ == "__main__":
    asyncio.run(main())
