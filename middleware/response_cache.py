"""Response caching middleware — exact-match cache for non-streaming requests."""

from __future__ import annotations

from typing import Any

from loguru import logger

from .base import Middleware
from .cache_utils import compute_request_hash


class ResponseCacheMiddleware(Middleware):
    """Cache non-streaming responses using SHA-256 request hashing.

    On cache hit, short-circuits the pipeline by returning the cached response
    from ``before_request``.  On miss, stores the response in
    ``after_response`` with a configurable TTL.

    Streaming requests are passed through without caching.
    """

    async def before_request(self, request_data: Any) -> Any:
        if not self.settings.enable_response_cache:
            return request_data

        if getattr(request_data, "stream", False):
            return request_data

        request_hash = compute_request_hash(request_data)

        cached = await self.storage.get_cached_response(request_hash)
        if cached is not None:
            logger.debug("CACHE_HIT: hash={}", request_hash[:12])
            return cached

        request_data._cache_hash = request_hash
        return request_data

    async def after_response(
        self, request_data: Any, response: Any, latency_ms: float
    ) -> Any:
        if not self.settings.enable_response_cache:
            return response

        if getattr(request_data, "stream", False):
            return response

        request_hash: str | None = getattr(request_data, "_cache_hash", None)
        if request_hash is None:
            return response

        await self.storage.store_cached_response(
            request_hash=request_hash,
            response_data=response,
            ttl_seconds=self.settings.cache_ttl_seconds,
        )
        await self.storage.evict_expired_cache()
        await self.storage.enforce_cache_max_entries(self.settings.cache_max_entries)

        logger.debug("CACHE_STORE: hash={} ttl={}s", request_hash[:12], self.settings.cache_ttl_seconds)
        return response
