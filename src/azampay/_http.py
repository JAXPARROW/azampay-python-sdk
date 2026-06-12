from __future__ import annotations

import json
from typing import Any

import httpx

from .exceptions import (
    AzamPayError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        return response.json()  # type: ignore[no-any-return]
    except (json.JSONDecodeError, ValueError):
        try:
            return {"message": response.text}
        except Exception:
            return {"message": "<unreadable response>"}


def handle_response(response: httpx.Response) -> Any:
    body = safe_json(response)
    status = response.status_code

    if status == 400:
        raise ValidationError(body.get("message", "Validation error"), status_code=400, response=body)
    if status == 401:
        raise AuthenticationError(body.get("message", "Unauthorized"), status_code=401, response=body)
    if status == 403:
        raise ForbiddenError(body.get("message", "Forbidden"), status_code=403, response=body)
    if status == 404:
        raise NotFoundError(body.get("message", "Not found"), status_code=404, response=body)
    if status == 429:
        raise RateLimitError(body.get("message", "Rate limit exceeded"), status_code=429, response=body)
    if status >= 500:
        raise ServerError(body.get("message", "Server error"), status_code=status, response=body)
    if not response.is_success:
        raise AzamPayError(body.get("message", "Request failed"), status_code=status, response=body)
    if isinstance(body, dict) and not body.get("success", True):
        raise AzamPayError(body.get("message", "Request failed"), status_code=status, response=body)

    return body
