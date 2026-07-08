"""Simple in-memory rate limit middleware."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply per-IP request rate limiting with minute window."""

    def __init__(self, app, requests_per_minute: int = 120):  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._requests_per_minute = requests_per_minute
        self._bucket: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if self._requests_per_minute <= 0:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        queue = self._bucket[ip]

        while queue and now - queue[0] > 60:
            queue.popleft()

        if len(queue) >= self._requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again in a minute."},
            )

        queue.append(now)
        return await call_next(request)
