"""Request logging middleware — records request metadata to storage."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import Middleware


class RequestLoggerMiddleware(Middleware):
    """Log request metadata to the storage layer after each response."""

    async def before_request(self, request_data: Any) -> Any:
        if not self.settings.enable_request_logging:
            return request_data
        return request_data

    async def after_response(
        self, request_data: Any, response: Any, latency_ms: float
    ) -> Any:
        if not self.settings.enable_request_logging:
            return response

        model = getattr(request_data, "model", None)
        await self.storage.log_request(
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=model,
            provider=None,
            tokens_in=None,
            tokens_out=None,
            latency_ms=latency_ms,
            cost_usd=None,
            cache_hit=False,
        )
        return response
