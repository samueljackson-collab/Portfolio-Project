"""Content and SEO automation primitives for the MonkAI marketing suite.

The real project would integrate with dedicated NLP models, SERP scrapers,

and analytics pipelines.  This module offers a deterministic, testable

facsimile that demonstrates how those systems interact.  The goal is to give

high-level workflows that feel realistic while remaining completely

self-contained for local execution."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Dict, Iterable, List, Sequence


def _stable_numeric(seed: str, *, minimum: int = 10, maximum: int = 1000) -> int:
    """Generate a deterministic pseudo-random integer for a given seed."""

    digest = sha256(seed.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16)
    return minimum + value % (maximum - minimum)


@dataclass
class KeywordMetrics:
    keyword: str
    search_volume: int
    keyword_difficulty: int
    intent: str
    opportunity_score: int


@dataclass
class KeywordResearchResult:
    topic: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    questions: List[str]
    metrics: List[KeywordMetrics]


class LocalKeywordAI:
    """Lightweight keyword research emulation."""

    QUESTION_STARTERS = ["how", "what", "why", "where", "when"]

    async def analyze(self, topic: str, seed_keywords: Sequence[str]) -> KeywordResearchResult:
        await asyncio.sleep(0)  # allow cooperative scheduling during tests

        normalized_seed = [kw.lower() for kw in seed_keywords]
        expanded = self._expand_keywords(topic, normalized_seed)
        metrics = [self._build_metrics(keyword, topic) for keyword in expanded]

        sorted_metrics = sorted(metrics, key=lambda item: item.opportunity_score, reverse=True)
        primary = [metric.keyword for metric in sorted_metrics[:5]]
        secondary = [metric.keyword for metric in sorted_metrics[5:10]]

        questions = self._generate_questions(topic, primary)

        return KeywordResearchResult(
            topic=topic,
            primary_keywords=primary,
            secondary_keywords=secondary,
            questions=questions,
            metrics=sorted_metrics,
        )

    def _expand_keywords(self, topic: str, seeds: Sequence[str]) -> List[str]:
        modifiers = ["guide", "techniques", "tools", "pricing", "reviews"]
        expanded = set(seeds)
        for seed in seeds:
            for modifier in modifiers:
                expanded.add(f"{seed} {modifier}")
        expanded.add(f"{topic.lower()} beginners")
        expanded.add(f"{topic.lower()} advanced")
        return sorted(expanded)

    def _build_metrics(self, keyword: str, topic: str) -> KeywordMetrics:
        base_seed = f"{topic}:{keyword}"
        volume = _stable_numeric(base_seed, minimum=120, maximum=4800)
        difficulty = _stable_numeric(base_seed + "-difficulty", minimum=12, maximum=92)
        intent_bucket = ["informational", "transactional", "navigational"]
        intent_index = _stable_numeric(base_seed + "-intent", minimum=0, maximum=len(intent_bucket))
        intent = intent_bucket[intent_index % len(intent_bucket)]
        opportunity = max(10, min(100, int((volume / max(difficulty, 1)) * 4)))
        return KeywordMetrics(
            keyword=keyword,
            search_volume=volume,
            keyword_difficulty=difficulty,
            intent=intent,
            opportunity_score=opportunity,
        )

    def _generate_questions(self, topic: str, keywords: Sequence[str]) -> List[str]:
        questions: List[str] = []
        for index, keyword in enumerate(keywords):
            starter = self.QUESTION_STARTERS[index % len(self.QUESTION_STARTERS)]
            questions.append(f"{starter.title()} {keyword}?")
        questions.append(f"What makes {topic.lower()} unique?")
        return questions


@dataclass
class OutlineSection:
    heading: str
    summary: str
    keyword_focus: List[str] = field(default_factory=list)
    word_count: int = 0


class OnPageAnalyzer:
    """Generates article outlines and draft content."""

    def plan_outline(
        self,
        topic: str,
        focus_keywords: Sequence[str],
        tone: str,
        target_word_count: int,
    ) -> List[OutlineSection]:
        normalized_keywords: List[str] = []
        for keyword in focus_keywords:
            text = str(keyword).strip()
            if text:
                normalized_keywords.append(text)
        if not normalized_keywords:
            normalized_keywords = [topic.lower()]

        sections: List[OutlineSection] = []
        intro_keywords = list(normalized_keywords[:2])
        sections.append(
            OutlineSection(
                heading=f"Introduction to {topic.title()}",
                summary="Establish the reader's intent and highlight the value proposition.",
                keyword_focus=intro_keywords,
                word_count=int(target_word_count * 0.12),
            )
        )

        body_sections = max(3, min(6, len(normalized_keywords)))
        per_section_words = int(target_word_count * 0.7 / body_sections)
        for index in range(body_sections):
            keyword = normalized_keywords[index % len(normalized_keywords)]
            keyword_slice = [
                normalized_keywords[(index + offset) % len(normalized_keywords)]
                for offset in range(min(2, len(normalized_keywords)))
            ]
            heading_keyword = keyword or topic.lower()
            sections.append(
                OutlineSection(
                    heading=f"{heading_keyword.title()} Strategies",
                    summary=(
                        f"Discuss actionable techniques for {heading_keyword} using a {tone} tone."
                    ),
                    keyword_focus=list(keyword_slice),
                    word_count=per_section_words,
                )
            )

        sections.append(
            OutlineSection(
                heading="Conclusion & Call-to-Action",
                summary="Summarize the transformation and recommend the next step.",
                keyword_focus=list(normalized_keywords[-2:]),
                word_count=int(target_word_count * 0.18),
            )
        )
        return sections

    def craft_content(
        self,
        outline: Sequence[OutlineSection],
        tone: str,
        research: KeywordResearchResult,
        target_word_count: int,
    ) -> str:
        paragraphs: List[str] = []
        keywords_iterator = self._cycle_keywords(
            research.primary_keywords + research.secondary_keywords
        )
        for section in outline:
            paragraph = self._build_paragraph(section, tone, keywords_iterator)
            paragraphs.append(paragraph)

        draft = "\n\n".join(paragraphs)
        current_words = len(draft.split())
        if current_words < target_word_count:
            filler = (
                "\n\n"
                "Further detail each step with customer stories, workshop insights, and "
                "artisan tips that prove domain authority."
            )
            draft += filler
        return draft

    def _cycle_keywords(self, keywords: Sequence[str]) -> Iterable[str]:
        while True:
            for keyword in keywords:
                yield keyword

    def _build_paragraph(
        self,
        section: OutlineSection,
        tone: str,
        keyword_source: Iterable[str],
    ) -> str:
        keyword_mentions = [next(keyword_source) for _ in range(min(3, len(section.keyword_focus)))]
        joined_keywords = ", ".join(keyword_mentions)
        return (
            f"## {section.heading}\n"
            f"{section.summary} Maintain a {tone} voice while weaving in {joined_keywords}. "
            "Illustrate the process with sensory language that highlights craftsmanship and reliability."
        )


class SiteCrawler:
    """Simulated on-site technical audit."""

    async def audit(self, topic: str, keywords: Sequence[str]) -> Dict[str, object]:
        await asyncio.sleep(0)
        crawl_depth = _stable_numeric(topic + "-crawl", minimum=3, maximum=12)
        return {
            "core_web_vitals": {
                "lcp": round(2.1 + (_stable_numeric(topic + "-lcp", minimum=0, maximum=100) / 1000), 2),
                "cls": round(0.05 + (_stable_numeric(topic + "-cls", minimum=0, maximum=50) / 1000), 3),
                "tti": round(1.8 + (_stable_numeric(topic + "-tti", minimum=0, maximum=150) / 1000), 2),
            },
            "internal_link_opportunities": [
                f"Add contextual link to '{keyword}' from related pillar pages." for keyword in keywords[:3]
            ],
            "schema_recommendations": [
                "Product", "HowTo", "FAQ"
            ],
            "crawl_depth": crawl_depth,
        }


class SERPMonitor:
    """Collects a synthetic search engine results snapshot."""

    async def snapshot(self, keywords: Sequence[str]) -> List[Dict[str, object]]:
        await asyncio.sleep(0)
        serp_data: List[Dict[str, object]] = []
        for keyword in keywords:
            headline_variants = [
                f"{keyword.title()} - TwistedMonk",
                f"{keyword.title()} Best Practices",
                f"{keyword.title()} Buying Guide",
            ]
            serp_data.append(
                {
                    "keyword": keyword,
                    "average_position": round(
                        _stable_numeric(keyword + "-rank", minimum=1, maximum=40) / 3, 1
                    ),
                    "competing_urls": [
                        f"https://example.com/{keyword.replace(' ', '-')}-guide",
                        f"https://example.com/{keyword.replace(' ', '-')}-shop",
                    ],
                    "headline_variants": headline_variants,
                }
            )
        return serp_data


class ContentAISuite:
    """End-to-end orchestrator for SEO content production."""

    def __init__(self) -> None:
        self.keyword_research = LocalKeywordAI()
        self.content_optimizer = OnPageAnalyzer()
        self.technical_audit = SiteCrawler()
        self.rank_tracker = SERPMonitor()

    async def generate_seo_content(
        self,
        topic: str,
        target_keywords: Sequence[str],
        tone: str = "professional",
        word_count: int = 800,
    ) -> Dict[str, object]:
        research_task = asyncio.create_task(
            self.keyword_research.analyze(topic, target_keywords)
        )
        audit_task = asyncio.create_task(self.technical_audit.audit(topic, target_keywords))

        research = await research_task
        outline = self.content_optimizer.plan_outline(topic, research.primary_keywords, tone, word_count)
        draft = self.content_optimizer.craft_content(outline, tone, research, word_count)
        serp_snapshot = await self.rank_tracker.snapshot(research.primary_keywords[:5])
        audit = await audit_task

        return {
            "topic": topic,
            "tone": tone,
            "target_word_count": word_count,
            "outline": [section.__dict__ for section in outline],
            "keywords": {
                "primary": research.primary_keywords,
                "secondary": research.secondary_keywords,
                "questions": research.questions,
                "metrics": [metric.__dict__ for metric in research.metrics],
            },
            "content": draft,
            "technical_audit": audit,
            "serp_snapshot": serp_snapshot,
        }
