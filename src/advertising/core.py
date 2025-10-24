"""Advertising intelligence utilities for the MonkAI toolkit."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, List, Optional


def _seed_value(*values: str, minimum: int = 10, maximum: int = 100) -> int:
    digest = sha256("::".join(values).encode("utf-8")).hexdigest()
    value = int(digest[:8], 16)
    return minimum + value % (maximum - minimum)


@dataclass
class AudiencePersona:
    name: str
    description: str
    top_values: List[str]
    preferred_channels: List[str]


class AdCreativeAI:
    """Produces on-brand ad copy variations."""

    def generate(
        self,
        product_info: Dict[str, object],
        tone: str = "enthusiastic",
        variations: int = 3,
    ) -> List[Dict[str, str]]:
        name = str(product_info.get("name", "Product"))
        raw_benefits = product_info.get("benefits") or []
        benefits: List[str] = []
        if isinstance(raw_benefits, str):
            normalized = raw_benefits.strip()
            if normalized:
                benefits = [normalized]
        elif isinstance(raw_benefits, Iterable):
            for item in raw_benefits:
                if item is None:
                    continue
                normalized = str(item).strip()
                if normalized:
                    benefits.append(normalized)
        elif raw_benefits is not None:
            normalized = str(raw_benefits).strip()
            if normalized:
                benefits = [normalized]
        if not benefits:
            benefits = ["premium craftsmanship"]
        creatives: List[Dict[str, str]] = []
        ctas = ["Shop Now", "Discover More", "Reserve Yours"]
        for index in range(variations):
            benefit = benefits[index % len(benefits)] if benefits else "premium craftsmanship"
            creatives.append(
                {
                    "headline": f"{name} built for {benefit}",
                    "primary_text": (
                        f"Experience {name} engineered with {benefit}. "
                        f"Our {tone} team crafts each piece to elevate every adventure."
                    ),
                    "cta": ctas[index % len(ctas)],
                    "visual_prompt": f"Lifestyle photo highlighting {name} with focus on {benefit}",
                }
            )
        return creatives


class DemographicAnalyzer:
    """Constructs lightweight audience personas."""

    def profile(self, product_info: Dict[str, object]) -> List[AudiencePersona]:
        product_type = str(product_info.get("type", "product")).title()
        price = float(product_info.get("price", 100.0))
        personas: List[AudiencePersona] = []

        personas.append(
            AudiencePersona(
                name="Performance Seekers",
                description=f"Consumers wanting reliable {product_type} built to last.",
                top_values=["durability", "safety", "premium materials"],
                preferred_channels=["instagram", "youtube", "reddit"],
            )
        )

        if price > 150:
            personas.append(
                AudiencePersona(
                    name="Luxury Enthusiasts",
                    description="Buyers prioritising artisanal quality over cost.",
                    top_values=["craftsmanship", "exclusivity", "heritage"],
                    preferred_channels=["facebook", "pinterest", "email"],
                )
            )
        else:
            personas.append(
                AudiencePersona(
                    name="Value Explorers",
                    description="Budget-conscious hobbyists comparing premium upgrades.",
                    top_values=["value", "reliability", "community"],
                    preferred_channels=["tiktok", "instagram", "discord"],
                )
            )
        return personas


class ROAPredictor:
    """Creates deterministic ROAS-focused budget guidance."""

    def estimate(
        self,
        product_info: Dict[str, object],
        creatives: List[Dict[str, str]],
        total_budget: float,
    ) -> Dict[str, float]:
        base = max(float(product_info.get("price", 100.0)), 1.0)
        spread = len(creatives)
        allocations: Dict[str, float] = {}
        for creative in creatives:
            headline = creative["headline"]
            performance_multiplier = _seed_value(headline, str(base), minimum=70, maximum=130) / 100
            allocations[headline] = round(total_budget * performance_multiplier / spread, 2)
        return allocations


class UnifiedManager:
    """Assembles cross-channel deployment suggestions."""

    def recommend(
        self,
        creatives: List[Dict[str, str]],
        personas: List[AudiencePersona],
        preferred_channels: Optional[List[str]] = None,
    ) -> List[Dict[str, object]]:
        plan: List[Dict[str, object]] = []
        for creative in creatives:
            persona = personas[_seed_value(creative["headline"], minimum=0, maximum=len(personas)) % len(personas)]
            channels = preferred_channels or persona.preferred_channels
            plan.append(
                {
                    "headline": creative["headline"],
                    "primary_channel": channels[0],
                    "supporting_channels": channels[1:],
                    "persona": persona.name,
                }
            )
        return plan


class AdvertisingAI:
    """High-level façade for campaign generation and optimization."""

    def __init__(self) -> None:
        self.creative_gen = AdCreativeAI()
        self.audience_ai = DemographicAnalyzer()
        self.bid_optimizer = ROAPredictor()
        self.cross_platform = UnifiedManager()

    def generate_ad_creatives(
        self,
        product_info: Dict[str, object],
        *,
        tone: str = "enthusiastic",
        budget: float = 3000.0,
        preferred_channels: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        creatives = self.creative_gen.generate(product_info, tone=tone)
        audience = self.audience_ai.profile(product_info)
        budget_plan = self.bid_optimizer.estimate(product_info, creatives, budget)
        channel_plan = self.cross_platform.recommend(creatives, audience, preferred_channels)
        return {
            "creatives": creatives,
            "audience_personas": [persona.__dict__ for persona in audience],
            "budget_plan": budget_plan,
            "channel_plan": channel_plan,
        }

    def optimize_campaigns(self, platform_data: Dict[str, Dict[str, float]]) -> Dict[str, object]:
        optimizations: List[Dict[str, object]] = []
        for platform, metrics in platform_data.items():
            cpa = metrics.get("cost_per_acquisition", 0.0)
            roas = metrics.get("roas", 1.0)
            adjustment = "increase" if roas > 3 and cpa < 25 else "decrease" if roas < 1.5 else "maintain"
            optimizations.append(
                {
                    "platform": platform,
                    "recommended_action": adjustment,
                    "notes": f"ROAS: {roas}, CPA: {cpa}",
                }
            )
        return {"optimizations": optimizations}
