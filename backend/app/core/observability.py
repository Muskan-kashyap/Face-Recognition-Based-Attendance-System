import time
import uuid
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_or_create_request_id(request) -> str:
    """Ensure request.state.request_id exists."""
    rid = getattr(getattr(request, "state", None), "request_id", None)
    if rid:
        return rid
    rid = str(uuid.uuid4())[:8]
    # request.state is settable
    request.state.request_id = rid
    return rid


class Metrics:
    """Tiny in-process metrics registry.

    - Not a full Prometheus client.
    - Exposes a /metrics text endpoint compatible with Prometheus scraping.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.request_total = 0
        self.error_total = 0
        self.latency_ms_sum = 0.0
        self.latency_ms_count = 0

    def observe_request(self, *, is_error: bool, latency_ms: float) -> None:
        self.request_total += 1
        if is_error:
            self.error_total += 1
        self.latency_ms_sum += float(latency_ms)
        self.latency_ms_count += 1

    def render_prometheus_text(self) -> str:
        # Gauges/counters style; keep it simple.
        avg_latency = (
            self.latency_ms_sum / self.latency_ms_count
            if self.latency_ms_count
            else 0.0
        )
        lines = [
            "# HELP fr_attendance_requests_total Total HTTP requests processed by this instance",
            "# TYPE fr_attendance_requests_total counter",
            f"fr_attendance_requests_total {self.request_total}",
            "# HELP fr_attendance_errors_total Total HTTP 4xx/5xx errors observed by this instance",
            "# TYPE fr_attendance_errors_total counter",
            f"fr_attendance_errors_total {self.error_total}",
            "# HELP fr_attendance_latency_ms_avg Average request latency in milliseconds",
            "# TYPE fr_attendance_latency_ms_avg gauge",
            f"fr_attendance_latency_ms_avg {avg_latency}",
            "",
        ]
        return "\n".join(lines)


metrics = Metrics()


def structured_log(message: str, *, request_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
    payload: Dict[str, Any] = {"msg": message}
    if request_id:
        payload["request_id"] = request_id
    if extra:
        payload.update(extra)

    # Using JSON-ish string for minimal deps.
    try:
        logger.info(payload)
    except Exception:
        # Fallback in case logger formatting fails
        logger.info(message)


def now_ms() -> float:
    return time.time() * 1000.0

