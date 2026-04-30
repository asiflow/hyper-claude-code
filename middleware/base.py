"""Abstract base class for middleware components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from config.settings import Settings
    from storage.database import Storage


class Middleware(ABC):
    """Base class for request/response middleware.

    Subclasses override ``before_request`` and/or ``after_response`` to
    intercept the proxy pipeline.
    """

    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    async def before_request(self, request_data: Any) -> Any:
        """Called before ``create_message``.

        Return the (possibly modified) *request_data* to continue the
        pipeline, or return a *response* object to short-circuit.
        """
        return request_data

    async def after_response(
        self, request_data: Any, response: Any, latency_ms: float
    ) -> Any:
        """Called after ``create_message`` with the response.

        Return the (possibly modified) response.
        """
        return response
