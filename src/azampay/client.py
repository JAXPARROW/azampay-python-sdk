from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
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
from .security import SecurityManager

_SANDBOX_BASE = "https://sandbox.azampay.co.tz"
_SANDBOX_AUTH = "https://authenticator-sandbox.azampay.co.tz"
_SANDBOX_DISBURSE = "https://api-disbursement-sandbox.azampay.co.tz"
_TEST_AUTH = "https://authenticator-test.azampay.co.tz"
_TEST_DISBURSE = "https://api-disbursement-test.azampay.co.tz"
_PRODUCTION_AUTH = "https://authenticator.azampay.co.tz"
_PRODUCTION_API = "https://checkout.azampay.co.tz"
_PRODUCTION_DISBURSE = "https://api-disbursement.azampay.co.tz"
_AUTH_PATH = "/AppRegistration/GenerateToken"
_TOKEN_TTL = 82800  # 23 hours (API TTL is 24 hours)
_RETRY_STATUSES = {500, 502, 503, 504}


def _safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        return response.json()  # type: ignore[no-any-return]
    except (json.JSONDecodeError, ValueError):
        try:
            return {"message": response.text}
        except Exception:
            return {"message": "<unreadable response>"}


def _backoff(attempt: int) -> None:
    time.sleep(2 ** (attempt - 1))


class AzamPayClient:
    """Synchronous AzamPay API client.

    Args:
        app_name:     Application name registered on the AzamPay portal.
        client_id:    OAuth client ID.
        client_secret: OAuth client secret.
        x_api_key:    Optional X-API-Key header value for API calls.
        sandbox:      When True, all requests target the sandbox environment.
        timeout:      HTTP request timeout in seconds (default 30).
        max_retries:  Maximum retry attempts on transient failures (default 3).
    """

    def __init__(
        self,
        app_name: str,
        client_id: str,
        client_secret: str,
        x_api_key: str | None = None,
        sandbox: bool = False,
        disburse_test: bool = False,
        rsa_public_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        token: str | None = None,
    ) -> None:
        self.app_name = app_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.x_api_key = x_api_key
        self.sandbox = sandbox
        self.rsa_public_key = rsa_public_key
        self.timeout = timeout
        self.max_retries = max_retries

        if disburse_test:
            self._auth_url = _TEST_AUTH
            self.disburse_url = _TEST_DISBURSE
        elif sandbox:
            self._auth_url = _SANDBOX_AUTH
            self.disburse_url = _SANDBOX_DISBURSE
        else:
            self._auth_url = _PRODUCTION_AUTH
            self.disburse_url = _PRODUCTION_DISBURSE
        self.base_url = _SANDBOX_BASE if sandbox else _PRODUCTION_API

        # Accept a pre-issued bearer token (e.g. from the developer portal)
        self._token: str | None = f"Bearer {token}" if token else None
        self._token_expires_at: float = time.monotonic() + _TOKEN_TTL if token else 0.0
        self._lock = threading.Lock()
        self._http = httpx.Client(timeout=timeout)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _authenticate(self) -> str:
        with self._lock:
            if self._token and time.monotonic() < self._token_expires_at:
                return self._token

            last_exc: Exception | None = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = self._http.post(
                        f"{self._auth_url}{_AUTH_PATH}",
                        json={
                            "appName": self.app_name,
                            "clientId": self.client_id,
                            "clientSecret": self.client_secret,
                        },
                    )
                except httpx.TransportError as exc:
                    last_exc = exc
                    if attempt < self.max_retries:
                        _backoff(attempt)
                    continue

                body = _safe_json(resp)

                if resp.status_code == 401:
                    raise AuthenticationError(
                        body.get("message", "Authentication failed"),
                        status_code=401,
                        response=body,
                    )
                if resp.status_code == 403:
                    raise ForbiddenError(
                        body.get("message", "Forbidden"),
                        status_code=403,
                        response=body,
                    )
                if resp.status_code in _RETRY_STATUSES and attempt < self.max_retries:
                    last_exc = AzamPayError(
                        body.get("message", "Server error"),
                        status_code=resp.status_code,
                        response=body,
                    )
                    _backoff(attempt)
                    continue

                if not resp.is_success or not body.get("success", True):
                    raise AzamPayError(
                        body.get("message", "Token generation failed"),
                        status_code=resp.status_code,
                        response=body,
                    )

                token = body["data"]["accessToken"]
                self._token = f"Bearer {token}"
                expire_str = (body.get("data") or {}).get("expire")
                if expire_str:
                    try:
                        expire_dt = datetime.fromisoformat(expire_str.replace("Z", "+00:00"))
                        ttl = (expire_dt - datetime.now(timezone.utc)).total_seconds() - 60
                        self._token_expires_at = time.monotonic() + max(ttl, 0)
                    except (ValueError, TypeError):
                        self._token_expires_at = time.monotonic() + _TOKEN_TTL
                else:
                    self._token_expires_at = time.monotonic() + _TOKEN_TTL
                return self._token

            raise (
                last_exc
                if isinstance(last_exc, AzamPayError)
                else AzamPayError(str(last_exc), response={})
            )

    # ------------------------------------------------------------------
    # Request dispatcher
    # ------------------------------------------------------------------

    def request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
        skip_checksum: bool = False,
    ) -> Any:
        token = self._authenticate()
        headers: dict[str, str] = {"Authorization": token}
        if self.x_api_key:
            headers["X-API-Key"] = self.x_api_key

        payload: dict[str, Any] | None = None
        if json is not None:
            payload = dict(json)
            if not skip_checksum and method.upper() in {"POST", "PUT", "PATCH"} and self.x_api_key:
                if "checksum" not in payload:
                    payload["checksum"] = SecurityManager.create_checksum(self.x_api_key, payload)

        url = f"{base_url or self.base_url}/{endpoint.lstrip('/')}"
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._http.request(
                    method,
                    url,
                    json=payload,
                    params=params,
                    headers=headers,
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                continue

            if resp.status_code in _RETRY_STATUSES and attempt < self.max_retries:
                last_exc = AzamPayError(
                    _safe_json(resp).get("message", "Server error"),
                    status_code=resp.status_code,
                    response=_safe_json(resp),
                )
                _backoff(attempt)
                continue

            return self._handle_response(resp)

        raise (
            last_exc
            if isinstance(last_exc, AzamPayError)
            else AzamPayError(str(last_exc), response={})
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        body = _safe_json(response)
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

        # Some AzamPay endpoints return HTTP 200 but success=false
        if isinstance(body, dict) and not body.get("success", True):
            raise AzamPayError(body.get("message", "Request failed"), status_code=status, response=body)

        return body

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_healthy(self) -> bool:
        """Return True if the API is reachable and credentials are valid."""
        try:
            self._authenticate()
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __repr__(self) -> str:
        env = "sandbox" if self.sandbox else "production"
        return f"{type(self).__name__}(app_name={self.app_name!r}, env={env!r})"

    def __enter__(self) -> "AzamPayClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
