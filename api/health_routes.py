"""Provider health endpoint — exposes circuit breaker state."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from .dependencies import require_api_key

health_router = APIRouter(tags=["health"])


@health_router.get("/v1/health/providers")
async def provider_health(
    request: Request, _auth: None = Depends(require_api_key),
) -> dict:
    """Return circuit breaker status for all tracked providers."""
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        return {"providers": [], "failover_enabled": False}

    from middleware.failover import FailoverMiddleware

    for mw in pipeline._middlewares:
        if isinstance(mw, FailoverMiddleware):
            return {
                "providers": [
                    breaker.status for breaker in mw.breakers.values()
                ],
                "failover_enabled": True,
            }

    return {"providers": [], "failover_enabled": False}
