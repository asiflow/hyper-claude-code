"""Per-provider circuit breaker with sliding-window error tracking."""

from __future__ import annotations

import enum
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any


class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class _Result:
    success: bool
    timestamp: float


@dataclass
class CircuitBreaker:
    """Sliding-window circuit breaker for a single provider.

    State transitions:
        CLOSED  -> OPEN       when error_rate >= threshold (window full)
        OPEN    -> HALF_OPEN  after cooldown expires
        HALF_OPEN -> CLOSED   on next success
        HALF_OPEN -> OPEN     on next failure (resets cooldown)
    """

    provider_id: str
    error_threshold: float = 0.5
    window_size: int = 10
    cooldown_seconds: float = 30.0
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _window: deque[_Result] = field(default_factory=deque, init=False)
    _opened_at: float = field(default=0.0, init=False)

    def allow_request(self) -> bool:
        """Return whether a request to this provider should proceed."""
        if self._state is CircuitState.CLOSED:
            return True
        if self._state is CircuitState.OPEN:
            if time.monotonic() - self._opened_at >= self.cooldown_seconds:
                self._state = CircuitState.HALF_OPEN
                return True
            return False
        # HALF_OPEN — allow exactly one probe request
        return True

    def record_success(self) -> None:
        now = time.monotonic()
        self._push(_Result(success=True, timestamp=now))
        if self._state is CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        now = time.monotonic()
        self._push(_Result(success=False, timestamp=now))
        if self._state is CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._opened_at = now
        elif self._state is CircuitState.CLOSED and self._should_trip():
            self._state = CircuitState.OPEN
            self._opened_at = now

    @property
    def status(self) -> dict[str, Any]:
        failures = sum(1 for r in self._window if not r.success)
        total = len(self._window)
        error_rate = failures / total if total else 0.0
        return {
            "provider": self.provider_id,
            "state": self._state.value,
            "error_rate": round(error_rate, 4),
            "window_fill": f"{total}/{self.window_size}",
        }

    def _push(self, result: _Result) -> None:
        self._window.append(result)
        while len(self._window) > self.window_size:
            self._window.popleft()

    def _should_trip(self) -> bool:
        total = len(self._window)
        if total < self.window_size:
            return False
        failures = sum(1 for r in self._window if not r.success)
        return (failures / total) >= self.error_threshold
