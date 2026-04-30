"""Cache management API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from loguru import logger

from .dependencies import get_settings, require_api_key

router = APIRouter(prefix="/v1/cache", tags=["cache"])


@router.get("/stats")
async def cache_stats(
    request: Request,
    _auth=Depends(require_api_key),
):
    """Return cache hit/miss counts, hit rate, and entry count."""
    storage = getattr(request.app.state, "storage", None)
    if storage is None:
        return {
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0,
            "entries": 0,
        }

    stats = await storage.get_cache_stats()
    entries = await storage.get_cache_entry_count()
    hits = stats["hits"]
    misses = stats["misses"]
    total = hits + misses
    hit_rate = (hits / total) if total > 0 else 0.0

    return {
        "hits": hits,
        "misses": misses,
        "hit_rate": round(hit_rate, 4),
        "entries": entries,
    }


@router.post("/clear")
async def cache_clear(
    request: Request,
    _auth=Depends(require_api_key),
):
    """Clear all cached responses."""
    storage = getattr(request.app.state, "storage", None)
    if storage is None:
        return {"cleared": 0}

    cleared = await storage.clear_cache()
    logger.info("CACHE_CLEAR: cleared={} entries", cleared)
    return {"cleared": cleared}
