"""Video production utilities for the MonkAI automation toolkit."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, Iterable, List


def _slugify(value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()[:8]
    safe = "-".join(part.lower() for part in value.split())
    return f"{safe}-{digest}"


@dataclass
class StoryboardScene:
    id: int
    narration: str
    visual_prompt: str
    duration_seconds: int
    beat: str


class OpenShotEngine:
    """Simplified editing pipeline and storyboard builder."""

    def create_storyboard(self, script: str, style: str) -> List[StoryboardScene]:
        sentences = [sentence.strip() for sentence in script.split(".") if sentence.strip()]
        if not sentences:
            raise ValueError("Script must contain at least one sentence.")

        scenes: List[StoryboardScene] = []
        beat_cycle = self._beat_cycle(style)
        for index, sentence in enumerate(sentences):
            scenes.append(
                StoryboardScene(
                    id=index + 1,
                    narration=sentence,
                    visual_prompt=f"{sentence} in {style} aesthetic",
                    duration_seconds=max(4, min(9, len(sentence.split()) // 2 + 4)),
                    beat=next(beat_cycle),
                )
            )
        return scenes

    def render_timeline(
        self,
        scenes: List[StoryboardScene],
        assets: List[Dict[str, str]],
        edit_plan: List[Dict[str, str]],
        style: str,
    ) -> str:
        timestamp = _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_stub = _slugify(f"{style}-{timestamp}-{len(scenes)}-scenes")
        return f"render/output/{file_stub}.mp4"

    def _beat_cycle(self, style: str) -> Iterable[str]:
        beats = ["hook", "build", "payoff"]
        if style.lower() == "tiktok":
            beats = ["pattern interrupt", "benefit", "call-to-action"]
        while True:
            for beat in beats:
                yield beat


class StableDiffusionGen:
    """Generates storyboard-aligned image prompts."""

    def generate_assets(self, scenes: List[StoryboardScene], style: str) -> List[Dict[str, str]]:
        assets: List[Dict[str, str]] = []
        for scene in scenes:
            prompt = (
                f"{scene.visual_prompt} | cinematic lighting | vibrant colors | style:{style}"
            )
            asset_path = f"assets/{_slugify(prompt)}.png"
            assets.append(
                {
                    "scene_id": scene.id,
                    "prompt": prompt,
                    "asset_path": asset_path,
                }
            )
        return assets


class WhisperTTSEngine:
    """Creates caption tracks from raw narration."""

    def generate_captions(self, script: str) -> List[Dict[str, object]]:
        segments: List[Dict[str, object]] = []
        sentences = [sentence.strip() for sentence in script.split(".") if sentence.strip()]
        cursor = 0.0
        for sentence in sentences:
            duration = max(2.5, min(6.0, len(sentence.split()) * 0.45))
            segments.append(
                {
                    "text": sentence,
                    "start": round(cursor, 2),
                    "end": round(cursor + duration, 2),
                }
            )
            cursor += duration
        return segments


class SmartCutAI:
    """Provides automatic edits and transitions."""

    def plan_edits(self, scenes: List[StoryboardScene]) -> List[Dict[str, str]]:
        edits: List[Dict[str, str]] = []
        for index, scene in enumerate(scenes):
            transition = "cut"
            if scene.beat == "pattern interrupt":
                transition = "glitch"
            elif scene.beat == "call-to-action":
                transition = "zoom"
            edits.append(
                {
                    "scene_id": scene.id,
                    "transition": transition,
                    "emphasis": "slow_motion" if index == 0 else "speed_ramp",
                }
            )
        return edits


class VideoAIPipeline:
    """Coordinates automated short-form video creation."""

    def __init__(self) -> None:
        self.editor = OpenShotEngine()
        self.ai_assets = StableDiffusionGen()
        self.captions = WhisperTTSEngine()
        self.auto_editor = SmartCutAI()

    def create_shorts(self, script: str, style: str = "tiktok") -> Dict[str, object]:
        storyboard = self.editor.create_storyboard(script, style)
        edit_plan = self.auto_editor.plan_edits(storyboard)
        assets = self.ai_assets.generate_assets(storyboard, style)
        captions = self.captions.generate_captions(script)
        video_path = self.editor.render_timeline(storyboard, assets, edit_plan, style)
        return {
            "video_path": video_path,
            "storyboard": [scene.__dict__ for scene in storyboard],
            "assets": assets,
            "captions": captions,
            "edit_plan": edit_plan,
            "metadata": {
                "style": style,
                "duration_seconds": sum(scene.duration_seconds for scene in storyboard),
            },
        }
