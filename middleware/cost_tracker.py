"""Cost tracking middleware — computes per-request cost and enforces budget caps."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse

from .base import Middleware
from .pricing import get_token_price


class CostTrackerMiddleware(Middleware):
    """Compute token cost after each response and enforce session budget caps."""

    async def before_request(self, request_data: Any) -> Any:
        if not self.settings.enable_cost_tracking:
            return request_data

        if self.settings.max_session_cost_usd is not None:
            summary = await self.storage.get_cost_summary("session")
            if summary["total_cost_usd"] >= self.settings.max_session_cost_usd:
                return JSONResponse(
                    status_code=429,
                    content={
                        "type": "error",
                        "error": {
                            "type": "rate_limit_error",
                            "message": (
                                f"Session cost budget exceeded: "
                                f"${summary['total_cost_usd']:.4f} / "
                                f"${self.settings.max_session_cost_usd:.4f}"
                            ),
                        },
                    },
                )

        return request_data

    async def after_response(
        self, request_data: Any, response: Any, latency_ms: float
    ) -> Any:
        if not self.settings.enable_cost_tracking:
            return response

        model = getattr(request_data, "model", None)
        provider = _extract_provider(model)
        model_name = _extract_model_name(model)

        tokens_in = _extract_tokens(response, "input")
        tokens_out = _extract_tokens(response, "output")

        input_price, output_price = get_token_price(provider, model_name)
        cost_usd = _compute_cost(tokens_in, tokens_out, input_price, output_price)

        await self.storage.log_request(
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=model,
            provider=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            cache_hit=False,
        )

        return response


def _extract_provider(model: str | None) -> str | None:
    """Extract provider id from a ``provider/model`` string."""
    if model is None or "/" not in model:
        return None
    return model.split("/", 1)[0]


def _extract_model_name(model: str | None) -> str | None:
    """Extract model name from a ``provider/model`` string."""
    if model is None or "/" not in model:
        return model
    return model.split("/", 1)[1]


def _extract_tokens(response: Any, direction: str) -> int | None:
    """Best-effort token count extraction from various response shapes."""
    usage = getattr(response, "usage", None)
    if usage is not None:
        if direction == "input":
            return getattr(usage, "input_tokens", None)
        return getattr(usage, "output_tokens", None)

    if isinstance(response, dict):
        usage_dict = response.get("usage")
        if isinstance(usage_dict, dict):
            if direction == "input":
                return usage_dict.get("input_tokens")
            return usage_dict.get("output_tokens")

    return None


def _compute_cost(
    tokens_in: int | None,
    tokens_out: int | None,
    input_price_per_1k: float,
    output_price_per_1k: float,
) -> float:
    """Compute cost in USD from token counts and per-1k prices."""
    cost = 0.0
    if tokens_in is not None:
        cost += (tokens_in / 1000.0) * input_price_per_1k
    if tokens_out is not None:
        cost += (tokens_out / 1000.0) * output_price_per_1k
    return cost
