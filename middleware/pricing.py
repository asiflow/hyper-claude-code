"""Provider pricing data for token cost estimation."""

from __future__ import annotations

_PRICE_PER_1K_TOKENS: dict[str, dict[str, tuple[float, float]]] = {
    "nvidia_nim": {
        "_default": (0.0, 0.0),
    },
    "open_router": {
        "_default": (0.001, 0.002),
    },
    "deepseek": {
        "_default": (0.00014, 0.00028),
    },
    "lmstudio": {
        "_default": (0.0, 0.0),
    },
    "llamacpp": {
        "_default": (0.0, 0.0),
    },
    "ollama": {
        "_default": (0.0, 0.0),
    },
}


def get_token_price(provider: str | None, model: str | None) -> tuple[float, float]:
    """Return ``(input_price_per_1k, output_price_per_1k)`` for a provider/model pair.

    Falls back to the provider default, then to ``(0.0, 0.0)`` for unknown providers.
    """
    if provider is None:
        return (0.0, 0.0)

    provider_prices = _PRICE_PER_1K_TOKENS.get(provider)
    if provider_prices is None:
        return (0.0, 0.0)

    if model is not None and model in provider_prices:
        return provider_prices[model]

    return provider_prices.get("_default", (0.0, 0.0))
