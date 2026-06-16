"""
Typed contracts for face/attendance pipeline stages.

These contracts are designed to:
- be stable over time
- carry explainable decision metadata (threshold, distances, candidates)
- return structured failures (instead of generic exceptions) where possible
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------- Success outputs ----------

@dataclass(frozen=True)
class DetectionOutput:
    image_present: bool
    face_detected: bool
    liveness_passed: Optional[bool] = None


@dataclass(frozen=True)
class AlignmentOutput:
    aligned: bool
    aligned_image_present: bool


@dataclass(frozen=True)
class EmbeddingOutput:
    embedding: List[float]
    model_name: str
    dim: int


@dataclass(frozen=True)
class VectorSearchCandidate:
    user_id: int
    score: float  # e.g., cosine distance (or similarity depending on implementation)


@dataclass(frozen=True)
class VectorSearchOutput:
    candidates: List[VectorSearchCandidate]
    top_k: int


@dataclass(frozen=True)
class ThresholdDecisionOutput:
    threshold: float
    accepted: bool
    best_candidate: Optional[VectorSearchCandidate] = None
    rejected_reason: Optional[str] = None


@dataclass(frozen=True)
class AttendanceDecisionOutput:
    user_id: int
    status: str  # on_time|late|early|absent|excused|manual_override
    is_live: int
    recognition_distance: Optional[float] = None
    match_explanation: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class AuditPayloadOutput:
    ref_type: str
    ref_id: int
    payload: Dict[str, Any]


# ---------- Structured errors ----------

@dataclass(frozen=True)
class PipelineError:
    stage: str
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
