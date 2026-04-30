"""Ordered middleware pipeline for request processing."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .base import Middleware


class Pipeline:
    """Execute an ordered sequence of middleware around a request handler."""

    def __init__(self, middlewares: list[Middleware] | None = None) -> None:
        self._middlewares: list[Middleware] = middlewares or []

    def add(self, mw: Middleware) -> None:
        self._middlewares.append(mw)

    async def process(
        self,
        request_data: Any,
        handler: Callable[[Any], Any],
    ) -> Any:
        for mw in self._middlewares:
            result = await mw.before_request(request_data)
            if result is not request_data:
                return result
            request_data = result

        start = time.perf_counter()
        response = handler(request_data)
        latency_ms = (time.perf_counter() - start) * 1000.0

        for mw in reversed(self._middlewares):
            response = await mw.after_response(request_data, response, latency_ms)

        return response
