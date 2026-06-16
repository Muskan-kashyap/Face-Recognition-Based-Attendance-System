from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class FaceMatchingConfig:
    """Single source of truth for face matching metric + threshold.

    NOTE: This repo currently implements matching using pgvector L2 distance.
    """

    metric: str
    threshold: float


def get_face_matching_config() -> FaceMatchingConfig:
    # Keep current behavior (L2 + threshold). Index/HNSW tuning can be aligned later.
    return FaceMatchingConfig(metric="l2", threshold=float(settings.FACE_DISTANCE_THRESHOLD))

