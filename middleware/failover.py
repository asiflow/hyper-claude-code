"""Provider failover middleware using per-provider circuit breakers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse
from loguru import logger

from config.settings import Settings

from .base import Middleware
from .circuit_breaker import CircuitBreaker


def _resolve_provider_id(request_data: Any, settings: Settings) -> str | None:
    """Derive the target provider id from an incoming request + settings."""
    model: str | None = getattr(request_data, "model", None)
    if model is None:
        return None
    provider_model_ref = settings.resolve_model(model)
    return Settings.parse_provider_type(provider_model_ref)


def _is_error_response(response: Any) -> bool:
    """Return True when the upstream response indicates a provider-level failure."""
    status: int | None = getattr(response, "status_code", None)
    if status is not None and status >= 500:
        return True
    if isinstance(response, Exception):
        return True
    return False


class FailoverMiddleware(Middleware):
    """Check circuit breakers before requests and record outcomes after."""

    def __init__(self, settings: Settings, storage: Any) -> None:
        super().__init__(settings, storage)
        self._breakers: dict[str, CircuitBreaker] = {}

    def _get_breaker(self, provider_id: str) -> CircuitBreaker:
        if provider_id not in self._breakers:
            self._breakers[provider_id] = CircuitBreaker(
                provider_id=provider_id,
                error_threshold=self.settings.failover_error_threshold,
                window_size=self.settings.failover_window_size,
                cooldown_seconds=self.settings.failover_cooldown_seconds,
            )
        return self._breakers[provider_id]

    @property
    def breakers(self) -> dict[str, CircuitBreaker]:
        return self._breakers

    async def before_request(self, request_data: Any) -> Any:
        if not self.settings.enable_provider_failover:
            return request_data

        provider_id = _resolve_provider_id(request_data, self.settings)
        if provider_id is None:
            return request_data

        breaker = self._get_breaker(provider_id)
        if breaker.allow_request():
            return request_data

        logger.warning(
            "Circuit breaker OPEN for provider '{}', attempting failover",
            provider_id,
        )

        chain = self.settings.failover_chains.get(provider_id, [])
        for alt_id in chain:
            alt_breaker = self._get_breaker(alt_id)
            if alt_breaker.allow_request():
                logger.info(
                    "Failover: '{}' -> '{}'", provider_id, alt_id,
                )
                request_data.__dict__["_failover_provider_id"] = alt_id
                return request_data

        logger.error(
            "All providers in failover chain exhausted for '{}'", provider_id,
        )
        return JSONResponse(
            status_code=503,
            content={
                "type": "error",
                "error": {
                    "type": "overloaded_error",
                    "message": (
                        f"Provider '{provider_id}' is unavailable and all "
                        f"failover alternatives are exhausted."
                    ),
                },
            },
        )

    async def after_response(
        self, request_data: Any, response: Any, latency_ms: float,
    ) -> Any:
        if not self.settings.enable_provider_failover:
            return response

        provider_id = getattr(request_data, "_failover_provider_id", None)
        if provider_id is None:
            provider_id = _resolve_provider_id(request_data, self.settings)
        if provider_id is None:
            return response

        breaker = self._get_breaker(provider_id)
        if _is_error_response(response):
            breaker.record_failure()
            error_type = str(getattr(response, "status_code", "unknown"))
            await self.storage.log_provider_error(
                provider_id=provider_id,
                error_type=error_type,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            logger.warning(
                "Provider '{}' failure recorded — circuit state: {}",
                provider_id,
                breaker.status["state"],
            )
        else:
            breaker.record_success()

        return response
