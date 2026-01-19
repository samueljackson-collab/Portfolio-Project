"""Celery tasks for AstraDup processing pipeline."""

from __future__ import annotations

import os
from typing import Dict, Optional

from celery import Celery

from src.engine.similarity_engine import SimilarityEngine


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery(
    "astradup",
    broker=os.getenv("CELERY_BROKER_URL", _redis_url()),
    backend=os.getenv("CELERY_RESULT_BACKEND", _redis_url()),
)


@celery_app.task(name="astradup.healthcheck")
def healthcheck() -> str:
    """Lightweight task to confirm the worker is responsive."""
    return "ok"


@celery_app.task(name="astradup.compute_similarity")
def compute_similarity(
    features1: Dict,
    features2: Dict,
    metadata1: Optional[Dict] = None,
    metadata2: Optional[Dict] = None,
) -> Dict:
    """Compute a multi-modal similarity payload from feature dictionaries."""
    engine = SimilarityEngine()
    visual_sim = engine.compute_visual_similarity(features1, features2)
    audio_sim = engine.compute_audio_similarity(features1, features2)
    metadata_sim = engine.compute_metadata_similarity(
        metadata1 or {}, metadata2 or {}
    )
    combined, confidence = engine.compute_combined_similarity(
        visual_sim,
        audio_sim,
        metadata_sim,
    )
    return {
        "visual_similarity": visual_sim,
        "audio_similarity": audio_sim,
        "metadata_similarity": metadata_sim,
        "combined_similarity": combined,
        "confidence": confidence,
    }
