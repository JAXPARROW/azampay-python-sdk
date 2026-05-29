from __future__ import annotations

from typing import Any


class AzamPayError(Exception):
    """Base exception for all AzamPay SDK errors."""

    def __init__(self, message: str, status_code: int = 0, response: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code}, message={self.args[0]!r})"


class AuthenticationError(AzamPayError):
    """Raised when credentials are invalid or token generation fails (HTTP 401)."""


class ForbiddenError(AzamPayError):
    """Raised when the request is not allowed for this account (HTTP 403)."""


class ValidationError(AzamPayError):
    """Raised when request data fails server-side validation (HTTP 400)."""


class NotFoundError(AzamPayError):
    """Raised when the requested resource does not exist (HTTP 404)."""


class RateLimitError(AzamPayError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class ServerError(AzamPayError):
    """Raised when AzamPay returns a 5xx response."""
