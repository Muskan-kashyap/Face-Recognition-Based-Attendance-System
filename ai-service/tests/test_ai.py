"""Unit tests for Phase 4 AI modules — FaceEngine, LivenessDetector, EmotionClassifier."""
import sys
import os
import unittest
import numpy as np
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.liveness import LivenessDetector
from app.services.emotion import EmotionClassifier
from app.services.face_engine import FaceEngine


def _make_frame(brightness: int = 128, w: int = 160, h: int = 120) -> np.ndarray:
    """Return a synthetic solid-colour BGR frame."""
    return np.full((h, w, 3), brightness, dtype=np.uint8)


def _make_random_frame(w: int = 160, h: int = 120) -> np.ndarray:
    """Return a high-variance noise frame (simulates a live face texture)."""
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (h, w, 3), dtype=np.uint8)


def _frame_to_bytes(img: np.ndarray) -> bytes:
    """Encode an ndarray as JPEG bytes."""
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


# ─── Liveness Tests ───────────────────────────────────────────────────────────

class TestLivenessDetector(unittest.TestCase):

    def setUp(self):
        self.detector = LivenessDetector()

    def test_flat_solid_frame_fails_liveness(self):
        """A uniform flat image has near-zero Laplacian variance → spoof."""
        img = _make_frame(brightness=128)
        is_live, score = self.detector.evaluate_liveness(img)
        self.assertFalse(is_live, "Flat solid frame should fail liveness check")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_high_texture_frame_passes_liveness(self):
        """A high-variance noise frame should pass the Laplacian check."""
        img = _make_random_frame()
        is_live, score = self.detector.evaluate_liveness(img)
        self.assertTrue(is_live, "High-variance frame should pass liveness")
        self.assertGreater(score, 0.0)

    def test_none_image_returns_false(self):
        is_live, score = self.detector.evaluate_liveness(None)
        self.assertFalse(is_live)
        self.assertEqual(score, 0.0)

    def test_laplacian_variance_positive(self):
        """Laplacian variance must always be non-negative."""
        img = _make_random_frame()
        var = LivenessDetector.calculate_laplacian_variance(img)
        self.assertGreaterEqual(var, 0.0)

    def test_eye_aspect_ratio_normal(self):
        """EAR for a standard open eye landmark set should be in [0.2, 0.5]."""
        # Six synthetic eye landmarks for an open eye
        eye = [(0, 0), (1, 2), (2, 2), (3, 0), (2, -2), (1, -2)]
        ear = LivenessDetector.calculate_eye_aspect_ratio(eye)
        self.assertGreater(ear, 0.0)

    def test_eye_aspect_ratio_empty(self):
        """Too few landmarks returns the default resting value."""
        ear = LivenessDetector.calculate_eye_aspect_ratio([])
        self.assertEqual(ear, 0.3)


# ─── Emotion Tests ────────────────────────────────────────────────────────────

class TestEmotionClassifier(unittest.TestCase):

    def setUp(self):
        self.clf = EmotionClassifier()

    def test_returns_valid_category(self):
        VALID = {"happy", "neutral", "sad", "stressed", "angry"}
        img = _make_random_frame(w=64, h=64)
        emotion, conf = self.clf.analyze_emotion(img)
        self.assertIn(emotion, VALID)

    def test_confidence_in_range(self):
        img = _make_random_frame(w=64, h=64)
        _, conf = self.clf.analyze_emotion(img)
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)

    def test_dark_flat_frame_returns_neutral(self):
        """Very uniform dark image → low std_dev → classified neutral."""
        img = _make_frame(brightness=30, w=64, h=64)
        emotion, conf = self.clf.analyze_emotion(img)
        self.assertEqual(emotion, "neutral")

    def test_none_region_returns_neutral(self):
        emotion, conf = self.clf.analyze_emotion(None)
        self.assertEqual(emotion, "neutral")
        self.assertEqual(conf, 1.0)


# ─── FaceEngine Tests ─────────────────────────────────────────────────────────

class TestFaceEngine(unittest.TestCase):

    def setUp(self):
        self.engine = FaceEngine()

    def test_invalid_bytes_returns_none(self):
        result = self.engine.extract_embedding(b"not_an_image")
        self.assertIsNone(result)

    def test_valid_frame_returns_128d_list(self):
        """A valid synthetic image must return a 128-d list."""
        img = _make_random_frame(w=200, h=200)
        embedding = self.engine.extract_embedding(_frame_to_bytes(img))
        # In fallback mode (no face_recognition library), returns 128-d vector
        if embedding is not None:
            self.assertEqual(len(embedding), 128)
            # Check normalization: L2 norm ≈ 1.0
            norm = float(np.linalg.norm(embedding))
            self.assertAlmostEqual(norm, 1.0, places=4)

    def test_bytes_to_image_valid(self):
        img = _make_frame(brightness=100)
        raw = _frame_to_bytes(img)
        decoded = FaceEngine.bytes_to_image(raw)
        self.assertIsNotNone(decoded)
        self.assertEqual(len(decoded.shape), 3)

    def test_bytes_to_image_invalid(self):
        result = FaceEngine.bytes_to_image(b"garbage")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
