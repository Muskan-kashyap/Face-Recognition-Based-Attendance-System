import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.observability import metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        start = time.time()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            latency_ms = (time.time() - start) * 1000.0
            status_code = response.status_code if response is not None else 500
            is_error = status_code >= 400
            metrics.observe_request(is_error=is_error, latency_ms=latency_ms)


