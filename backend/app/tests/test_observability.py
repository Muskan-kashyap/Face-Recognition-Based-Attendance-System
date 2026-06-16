from types import SimpleNamespace

import os
import sys

# Ensure project import path is correct when running `pytest` from different working dirs.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.observability import Metrics, get_or_create_request_id



class DummyRequest:
    def __init__(self):
        self.state = SimpleNamespace()


def test_get_or_create_request_id_creates_when_missing():
    r = DummyRequest()
    # state.request_id not set
    rid = get_or_create_request_id(r)
    assert isinstance(rid, str)
    assert len(rid) > 0
    assert r.state.request_id == rid


def test_metrics_render_prometheus_text_contains_counters():
    m = Metrics()
    m.observe_request(is_error=False, latency_ms=10.0)
    text = m.render_prometheus_text()
    assert "fr_attendance_requests_total" in text
    assert "fr_attendance_errors_total" in text
    assert "fr_attendance_latency_ms_avg" in text

