import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from main import app
from app.api.deps import get_current_active_user, get_db


# =====================================================
# TEST CLIENT
# =====================================================

client = TestClient(app)


# =====================================================
# MOCK USERS
# =====================================================

class DummyRole:
    name = "Employee"


class DummyShift:
    start_time = datetime(2025, 1, 1, 9, 0).time()
    grace_period_mins = 5
    buffer_mins = 15


class MockUser:
    id = 1
    org_id = "test-org-uuid"
    role = DummyRole()
    shift = DummyShift()


def override_get_current_active_user():
    return MockUser()


def override_get_db():
    session = MagicMock()
    yield session


app.dependency_overrides[get_current_active_user] = (
    override_get_current_active_user
)
app.dependency_overrides[get_db] = override_get_db


# =====================================================
# REDIS MOCK
# =====================================================

import app.core.rate_limit


class MockPipeline:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def incr(self, *args, **kwargs):
        pass

    def expire(self, *args, **kwargs):
        pass

    async def execute(self):
        return [1]


class MockRedisClient:
    def pipeline(self, *args, **kwargs):
        return MockPipeline()


app.core.rate_limit.redis_client = MockRedisClient()


# =====================================================
# ATTENDANCE CONTROLLER MOCK
# =====================================================

from app.services.attendance_controller import attendance_controller


class MockAttendanceLog:
    id = 100
    user_id = 1
    status = "on_time"
    check_in = datetime.now(timezone.utc)
    check_out = None
    emotion = "happy"
    is_live = 1
    recognition_distance = 0.2
    source = "edge"
    created_at = datetime.now(timezone.utc)


attendance_controller.log_check_in = MagicMock(
    return_value=MockAttendanceLog()
)


# =====================================================
# SUCCESSFUL CHECK-IN
# =====================================================

def test_checkin_success():

    from app.services.face_engine import face_engine
    from app.services.liveness import liveness_service
    from app.repositories.attendance_repo import attendance_repo

    liveness_service.detect_liveness = MagicMock(
        return_value=(True, 0.98)
    )

    face_engine.get_embedding = MagicMock(
        return_value=[0.1] * 128
    )

    face_engine.get_emotion = MagicMock(
        return_value="happy"
    )

    attendance_repo.find_user_by_face = MagicMock()

    mock_match = MagicMock()
    mock_match.user_id = 1

    attendance_repo.find_user_by_face.return_value = mock_match

    response = client.post(
        "/api/v1/attendance/check-in",
        json={
            "image_base64": "ZHVtbXk=",
            "source": "edge"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == 1
    assert data["status"] == "on_time"


# =====================================================
# SPOOF ATTACK
# =====================================================

def test_checkin_spoof_rejected():

    from app.services.face_engine import face_engine
    from app.services.liveness import liveness_service

    liveness_service.detect_liveness = MagicMock(
        return_value=(False, 0.10)
    )

    face_engine.get_embedding = MagicMock(
        return_value=[0.1] * 128
    )

    response = client.post(
        "/api/v1/attendance/check-in",
        json={
            "image_base64": "ZHVtbXk=",
            "source": "edge"
        }
    )

    assert response.status_code in [401, 403]


# =====================================================
# NO FACE DETECTED
# =====================================================

def test_checkin_no_face_detected():

    from app.services.face_engine import face_engine
    from app.services.liveness import liveness_service

    liveness_service.detect_liveness = MagicMock(
        return_value=(True, 0.98)
    )

    face_engine.get_embedding = MagicMock(
        return_value=None
    )

    response = client.post(
        "/api/v1/attendance/check-in",
        json={
            "image_base64": "ZHVtbXk=",
            "source": "edge"
        }
    )

    assert response.status_code in [400, 404]


# =====================================================
# UNKNOWN FACE
# =====================================================

def test_checkin_unknown_face():

    from app.services.face_engine import face_engine
    from app.services.liveness import liveness_service
    from app.repositories.attendance_repo import attendance_repo

    liveness_service.detect_liveness = MagicMock(
        return_value=(True, 0.98)
    )

    face_engine.get_embedding = MagicMock(
        return_value=[0.1] * 128
    )

    attendance_repo.find_user_by_face = MagicMock(
        return_value=None
    )

    response = client.post(
        "/api/v1/attendance/check-in",
        json={
            "image_base64": "ZHVtbXk=",
            "source": "edge"
        }
    )

    assert response.status_code in [400, 404]

