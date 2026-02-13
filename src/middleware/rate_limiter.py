"""In-memory sliding window rate limiter for SSE transport."""

from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if a request is allowed. Returns (allowed, retry_after_seconds)."""
        now = time.time()
        self._cleanup(key, now)

        if len(self._requests[key]) >= self.max_requests:
            oldest = self._requests[key][0]
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, retry_after

        self._requests[key].append(now)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that applies rate limiting per client IP."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = self.limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response
