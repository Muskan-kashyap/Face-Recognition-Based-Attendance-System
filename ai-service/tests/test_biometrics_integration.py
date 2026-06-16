import base64
import os
import unittest

import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError

# Prefer a dedicated test database for integration tests.
# Use TEST_DATABASE_URL first, otherwise fall back to existing DATABASE_URL if set.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://dbadmin:SecretPassword123@localhost:5432/face_attendance_test"),
)
# Ensure the AI service uses the configured database for its DB dependency.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


def ensure_database(url: str):
    parsed = make_url(url)
    db_name = parsed.database
    if not db_name:
        raise ValueError("Database URL must contain a database name")

    admin_db = "postgres" if db_name != "postgres" else "template1"
    admin_url = parsed.set(database=admin_db)
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with admin_engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": db_name})
            if result.scalar() is None:
                conn.execute(text(f"CREATE DATABASE \"{db_name}\""))
    finally:
        admin_engine.dispose()


def prepare_test_db(url: str):
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS users ("
                    "id SERIAL PRIMARY KEY, "
                    "full_name VARCHAR(255) NOT NULL, "
                    "org_id VARCHAR(255) NOT NULL, "
                    "is_deleted INT NOT NULL DEFAULT 0"
                    ")"
                )
            )
        engine.dispose()
        return True, None
    except OperationalError as exc:
        return False, str(exc)


try:
    ensure_database(TEST_DATABASE_URL)
    db_ready, db_error = prepare_test_db(TEST_DATABASE_URL)
except Exception as exc:
    db_ready = False
    db_error = str(exc)


from app.core.dependencies import get_current_user_claims
from app.db.database import Base, engine as app_engine
from app.main import app
import app.models.models as models  # ensure ORM models are registered with Base


SKIP_REASON = f"PostgreSQL test DB unavailable: {db_error}" if not db_ready else ""


class TestBiometricsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not db_ready:
            raise unittest.SkipTest(SKIP_REASON)

        Base.metadata.create_all(bind=app_engine)
        app.dependency_overrides[get_current_user_claims] = lambda: {
            "sub": 1,
            "type": "access",
            "permissions": ["biometrics.enroll"],
            "org_id": "test-org",
        }
        # Allow integration tests to bypass real image decoding and operate on a synthetic test image.
        import app.routers.biometrics as biometrics
        biometrics._decode_image_bytes = lambda payload: base64.b64decode(payload)
        biometrics._bytes_to_bgr = lambda image_bytes: np.zeros((100, 100, 3), dtype=np.uint8)

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_current_user_claims, None)
        with app_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE face_embeddings, users RESTART IDENTITY CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS users"))
            Base.metadata.drop_all(bind=app_engine)

    def setUp(self):
        with app_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE face_embeddings, users RESTART IDENTITY CASCADE"))

    def _base64_image(self):
        return base64.b64encode(b"real-integration-image-bytes").decode("utf-8")

    def test_enroll_face_persists_embedding_to_real_db(self):
        self._patch_ai_services(liveness_score=0.92, embedding=[0.01] * 128)

        response = self.client.post(
            "/api/v1/biometrics/enroll",
            json={"user_id": 7, "image_base64": self._base64_image()},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "enrolled")
        self.assertEqual(data["user_id"], 7)
        self.assertEqual(data["model_name"], "ArcFace")
        self.assertGreater(data["liveness_score"], 0.0)

        with app_engine.connect() as conn:
            row = conn.execute(
                text("SELECT user_id, model_name, is_active FROM face_embeddings WHERE user_id = :uid"),
                {"uid": 7},
            ).one_or_none()

        self.assertIsNotNone(row)
        self.assertEqual(row.user_id, 7)
        self.assertEqual(row.model_name, "ArcFace")
        self.assertEqual(row.is_active, 1)

    def test_verify_face_identifies_enrolled_user_in_real_db(self):
        self._patch_ai_services(liveness_score=0.97, embedding=[0.02] * 128)

        with app_engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (full_name, org_id, is_deleted) "
                    "VALUES (:full_name, :org_id, 0)"
                ),
                {"full_name": "Integration User", "org_id": "test-org"},
            )
            user_id = conn.execute(text("SELECT id FROM users WHERE org_id = :org_id"), {"org_id": "test-org"}).scalar()
            self.assertIsNotNone(user_id)

        enroll_response = self.client.post(
            "/api/v1/biometrics/enroll",
            json={"user_id": user_id, "image_base64": self._base64_image()},
        )
        self.assertEqual(enroll_response.status_code, 201)

        verify_response = self.client.post(
            "/api/v1/biometrics/verify",
            json={"image_base64": self._base64_image(), "org_id": "test-org"},
        )

        self.assertEqual(verify_response.status_code, 200)
        verified = verify_response.json()
        self.assertEqual(verified["status"], "verified")
        self.assertEqual(verified["user_id"], user_id)
        self.assertEqual(verified["full_name"], "Integration User")
        self.assertEqual(verified["distance"], 0.0)

    def _patch_ai_services(self, liveness_score: float, embedding: list[float]):
        import app.routers.biometrics as biometrics

        biometrics._liveness.evaluate_liveness = lambda img: (True, liveness_score)
        biometrics._face_engine.extract_embedding = lambda image_bytes: embedding
        biometrics._emotion.analyze_emotion = lambda img: ("neutral", 0.94)


if __name__ == "__main__":
    unittest.main()
