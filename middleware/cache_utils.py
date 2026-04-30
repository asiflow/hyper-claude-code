"""Request hashing utilities for response caching."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_request_hash(request_data: Any) -> str:
    """Compute a deterministic SHA-256 hash of the semantically meaningful request fields.

    Includes: model, messages, system, tools.
    Excludes: stream, metadata, request IDs, and other ephemeral fields.
    """
    normalized: dict[str, Any] = {}

    if model := getattr(request_data, "model", None):
        normalized["model"] = model

    if (messages := getattr(request_data, "messages", None)) is not None:
        normalized["messages"] = _normalize_value(messages)

    if (system := getattr(request_data, "system", None)) is not None:
        normalized["system"] = _normalize_value(system)

    if (tools := getattr(request_data, "tools", None)) is not None:
        normalized["tools"] = _normalize_value(tools)

    serialized = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _normalize_value(value: Any) -> Any:
    """Recursively normalize a value for deterministic JSON serialization."""
    if isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if hasattr(value, "model_dump"):
        return _normalize_value(value.model_dump())
    return value
