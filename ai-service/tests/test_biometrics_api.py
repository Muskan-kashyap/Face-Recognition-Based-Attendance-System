import base64
import unittest

import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.routers import biometrics


class DummyDB:
    def __init__(self, row=None):
        self.row = row
        self.executed = []
        self.committed = False

    def execute(self, statement, params=None):
        self.executed.append((statement, params))
        return self

    def fetchone(self):
        return self.row

    def commit(self):
        self.committed = True


class DummyMatch:
    def __init__(self, user_id, full_name, distance):
        self.user_id = user_id
        self.full_name = full_name
        self.distance = distance


class TestBiometricsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.dummy_db = DummyDB()

        biometrics._decode_image_bytes = lambda payload: base64.b64decode(payload)
        biometrics._bytes_to_bgr = lambda image_bytes: np.zeros((100, 100, 3), dtype=np.uint8)

        # Override DB and auth dependencies
        def override_db():
            yield self.dummy_db

        app.dependency_overrides[biometrics.get_db] = override_db
        app.dependency_overrides[biometrics.get_current_user_claims] = lambda: {
            "sub": 1,
            "type": "access",
            "permissions": ["biometrics.enroll"],
            "org_id": "test-org",
        }

    def tearDown(self):
        app.dependency_overrides.pop(biometrics.get_db, None)
        app.dependency_overrides.pop(biometrics.get_current_user_claims, None)

    def _base64_image(self):
        raw = b"fake-image-bytes"
        return base64.b64encode(raw).decode("utf-8")

    def test_verify_face_requires_liveness(self):
        biometrics._liveness.evaluate_liveness = lambda img: (False, 0.12)
        biometrics._face_engine.extract_embedding = lambda image_bytes: [0.01] * 128
        biometrics._emotion.analyze_emotion = lambda img: ("neutral", 0.95)
        self.dummy_db.row = None

        response = self.client.post(
            "/api/v1/biometrics/verify",
            json={"image_base64": self._base64_image(), "org_id": "test-org"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("liveness check failed", response.json()["detail"])

    def test_verify_face_returns_unknown_when_no_match(self):
        biometrics._liveness.evaluate_liveness = lambda img: (True, 0.87)
        biometrics._face_engine.extract_embedding = lambda image_bytes: [0.01] * 128
        biometrics._emotion.analyze_emotion = lambda img: ("happy", 0.78)
        self.dummy_db.row = None

        response = self.client.post(
            "/api/v1/biometrics/verify",
            json={"image_base64": self._base64_image(), "org_id": "test-org"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unknown")
        self.assertIsNone(data["user_id"])
        self.assertIsNone(data["distance"])
        self.assertEqual(data["dominant_emotion"], "happy")

    def test_verify_face_returns_verified_when_match_found(self):
        biometrics._liveness.evaluate_liveness = lambda img: (True, 0.96)
        biometrics._face_engine.extract_embedding = lambda image_bytes: [0.02] * 128
        biometrics._emotion.analyze_emotion = lambda img: ("sad", 0.43)
        self.dummy_db.row = DummyMatch(user_id=42, full_name="Alice Example", distance=0.23)

        response = self.client.post(
            "/api/v1/biometrics/verify",
            json={"image_base64": self._base64_image(), "org_id": "test-org"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "verified")
        self.assertEqual(data["user_id"], 42)
        self.assertAlmostEqual(data["distance"], 0.23, places=4)
        self.assertEqual(data["dominant_emotion"], "sad")

    def test_enroll_face_rejects_liveness(self):
        biometrics._liveness.evaluate_liveness = lambda img: (False, 0.14)
        biometrics._face_engine.extract_embedding = lambda image_bytes: [0.01] * 128
        self.dummy_db.executed.clear()

        response = self.client.post(
            "/api/v1/biometrics/enroll",
            json={"user_id": 99, "image_base64": self._base64_image()},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("liveness check failed", response.json()["detail"])
        self.assertFalse(self.dummy_db.committed)
        self.assertEqual(len(self.dummy_db.executed), 0)

    def test_enroll_face_rejects_missing_embedding(self):
        biometrics._liveness.evaluate_liveness = lambda img: (True, 0.82)
        biometrics._face_engine.extract_embedding = lambda image_bytes: None
        self.dummy_db.executed.clear()

        response = self.client.post(
            "/api/v1/biometrics/enroll",
            json={"user_id": 99, "image_base64": self._base64_image()},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("No face detected", response.json()["detail"])
        self.assertFalse(self.dummy_db.committed)
        self.assertEqual(len(self.dummy_db.executed), 0)

    def test_enroll_face_succeeds_and_commits(self):
        biometrics._liveness.evaluate_liveness = lambda img: (True, 0.91)
        biometrics._face_engine.extract_embedding = lambda image_bytes: [0.02] * 128
        self.dummy_db.executed.clear()

        response = self.client.post(
            "/api/v1/biometrics/enroll",
            json={"user_id": 99, "image_base64": self._base64_image()},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "enrolled")
        self.assertEqual(data["user_id"], 99)
        self.assertEqual(data["model_name"], "ArcFace")
        self.assertGreater(data["liveness_score"], 0.0)
        self.assertTrue(self.dummy_db.committed)
        self.assertEqual(len(self.dummy_db.executed), 2)
        self.assertIn("UPDATE face_embeddings SET is_active = 0 WHERE user_id = :uid", str(self.dummy_db.executed[0][0]))
        self.assertIn("INSERT INTO face_embeddings", str(self.dummy_db.executed[1][0]))


if __name__ == "__main__":
    unittest.main()
