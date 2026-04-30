"""Cost summary API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request

from .dependencies import get_settings, require_api_key

cost_router = APIRouter()


@cost_router.get("/v1/cost")
async def get_cost_summary(
    request: Request,
    _auth=Depends(require_api_key),
):
    """Return cost summaries for session, daily, and monthly periods."""
    storage = getattr(request.app.state, "storage", None)
    if storage is None:
        raise HTTPException(
            status_code=503,
            detail="Cost tracking requires enable_middleware_pipeline=true",
        )

    settings = get_settings()
    if not settings.enable_cost_tracking:
        raise HTTPException(
            status_code=404,
            detail="Cost tracking is not enabled (set ENABLE_COST_TRACKING=true)",
        )

    session = await storage.get_cost_summary("session")
    daily = await storage.get_cost_summary("daily")
    monthly = await storage.get_cost_summary("monthly")

    return {
        "session": session,
        "daily": daily,
        "monthly": monthly,
        "budget": {
            "max_session_cost_usd": settings.max_session_cost_usd,
            "session_remaining_usd": (
                max(0.0, settings.max_session_cost_usd - session["total_cost_usd"])
                if settings.max_session_cost_usd is not None
                else None
            ),
        },
    }
