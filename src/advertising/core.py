"""Core advertising helpers used across the portfolio tests."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict, List


class AdCreativeAI:
    """Generate lightweight advertising copy for portfolio demos."""

    DEFAULT_HEADLINE_TEMPLATE = "{product}: {benefits}"
    DEFAULT_COPY_TEMPLATE = (
        "Discover {benefits} with {product}. This {tone} message was generated "
        "by the AdCreativeAI helper."
    )

    def __init__(
        self,
        *,
        headline_template: str | None = None,
        copy_template: str | None = None,
        default_tone: str = "friendly",
    ) -> None:
        self.headline_template = headline_template or self.DEFAULT_HEADLINE_TEMPLATE
        self.copy_template = copy_template or self.DEFAULT_COPY_TEMPLATE
        self.default_tone = default_tone

    def _normalize_benefits(self, benefits: Any) -> List[str]:
        """Ensure benefits are stored as a list of human-friendly strings."""

        if benefits is None:
            return []

        if isinstance(benefits, str):
            candidates: Iterable[Any] = [benefits]
        elif isinstance(benefits, Iterable):
            candidates = list(benefits)
        else:
            candidates = [benefits]

        normalized: List[str] = []
        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip()
            if text:
                normalized.append(text)
        return normalized

    def generate(self, product_name: str, benefits: Any, tone: str | None = None) -> Dict[str, Any]:
        """Return a dictionary containing the generated marketing assets."""

        tone_value = (tone or self.default_tone).strip() or self.default_tone
        product_label = str(product_name).strip() or "Unnamed Product"
        benefit_list = self._normalize_benefits(benefits)

        if benefit_list:
            benefits_phrase = ", ".join(benefit_list)
        else:
            benefits_phrase = "standout benefits"

        headline = self.headline_template.format(
            product=product_label, benefits=benefits_phrase, tone=tone_value
        )
        copy = self.copy_template.format(product=product_label, benefits=benefits_phrase, tone=tone_value)

        return {
            "headline": headline,
            "copy": copy,
            "tone": tone_value,
            "benefits": benefit_list,
        }
