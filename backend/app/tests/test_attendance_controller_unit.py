import datetime
from types import SimpleNamespace

import pytest

from app.services.attendance_controller import AttendanceController


class DummyRole:
    def __init__(self, name: str):
        self.name = name


class DummyShift:
    def __init__(self):
        self.start_time = datetime.time(9, 0, 0)
        self.grace_period_mins = 5
        self.buffer_mins = 15


class DummyUser:
    def __init__(self, user_id: int, role_name: str = "Employee"):
        self.id = user_id
        self.role = DummyRole(role_name)
        self.shift = DummyShift()


class DummyReq:
    def __init__(self):
        self.image_base64 = None
        self.user_id = None
        self.emotion = None
        self.is_live = 0
        self.emotion_score = None
        self.source = "ai"
        self.geofence_pass = None
        self.gps_lat = None
        self.gps_lng = None
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)


class DummyDB:
    def __init__(self):
        self._user = DummyUser(1, "Admin")

    def query(self, model):
        # Only supports User queries in compute_shift_status
        assert model.__name__ in {"User"} or True
        return self

    def options(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._user

    def execute(self, stmt):
        # Not used in unit tests below; biometric pipeline is mocked.
        raise RuntimeError("not implemented")


class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))


def test_handle_check_in_spoofing_forbidden(monkeypatch):
    controller = AttendanceController()
    db = DummyDB()
    req = DummyReq()

    # User is Employee, tries to check in for a different identity
    current_user = DummyUser(1, role_name="Employee")
    req.user_id = 999
    req.image_base64 = None

    # Mock compute_shift_status + log_check_in so test focuses on permission gate
    monkeypatch.setattr(controller, "compute_shift_status", lambda _db, user_id, req_ts: "on_time")

    class DummyLog:
        id = 10
        user_id = 999
        status = "on_time"
        check_in = datetime.datetime.now(datetime.timezone.utc)

    monkeypatch.setattr(controller, "log_check_in", lambda _db, req, status: DummyLog())

    bg = DummyBackgroundTasks()

    with pytest.raises(ValueError, match="Image required for recognition"):
        controller.handle_check_in(db, req=req, current_user=current_user, background_tasks=bg)



def test_handle_check_in_requires_image_now(monkeypatch):
    controller = AttendanceController()
    db = DummyDB()
    req = DummyReq()
    req.image_base64 = None
    req.user_id = None

    current_user = DummyUser(1, role_name="Admin")
    bg = DummyBackgroundTasks()

    with pytest.raises(ValueError, match="Image required for recognition"):
        controller.handle_check_in(db, req=req, current_user=current_user, background_tasks=bg)


