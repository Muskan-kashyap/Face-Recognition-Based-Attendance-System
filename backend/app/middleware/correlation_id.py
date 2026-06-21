from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagate and expose correlation id.

    Requirements (Phase 4.2.1):
    - generate UUID if missing
    - reuse inbound X-Correlation-ID
    - attach to request.state
    - return response header
    """

    async def dispatch(self, request: Request, call_next):
        incoming: Optional[str] = request.headers.get(CORRELATION_ID_HEADER)
        correlation_id = incoming.strip() if incoming and incoming.strip() else str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        response: Response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response

