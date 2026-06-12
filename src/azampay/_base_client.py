from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from ._constants import (
    _AUTH_PATH,
    _PRODUCTION_API,
    _PRODUCTION_AUTH,
    _PRODUCTION_DISBURSE,
    _SANDBOX_AUTH,
    _SANDBOX_BASE,
    _SANDBOX_DISBURSE,
    _TEST_AUTH,
    _TEST_DISBURSE,
    _TOKEN_TTL,
)
from .security import SecurityManager


class BaseClient:
    """Shared initialisation and request-building logic for sync and async clients.

    Concrete subclasses supply the transport layer (httpx.Client or httpx.AsyncClient)
    and implement ``_authenticate()``, ``request()``, ``close()``, and ``is_healthy()``.
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

        self._token: str | None = f"Bearer {token}" if token else None
        self._token_expires_at: float = time.monotonic() + _TOKEN_TTL if token else 0.0

    def __repr__(self) -> str:
        env = "sandbox" if self.sandbox else "production"
        return f"{type(self).__name__}(app_name={self.app_name!r}, env={env!r})"

    # ------------------------------------------------------------------
    # Request-building helpers (used by both sync and async subclasses)
    # ------------------------------------------------------------------

    def _auth_endpoint(self) -> str:
        return f"{self._auth_url}{_AUTH_PATH}"

    def _auth_payload(self) -> dict[str, str]:
        return {
            "appName": self.app_name,
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }

    def _parse_token_expiry(self, body: dict[str, Any]) -> float:
        expire_str = (body.get("data") or {}).get("expire")
        if expire_str:
            try:
                expire_dt = datetime.fromisoformat(expire_str.replace("Z", "+00:00"))
                ttl = (expire_dt - datetime.now(timezone.utc)).total_seconds() - 60
                return time.monotonic() + max(ttl, 0)
            except (ValueError, TypeError):
                pass
        return time.monotonic() + _TOKEN_TTL

    def _build_headers(self, token: str) -> dict[str, str]:
        headers: dict[str, str] = {"Authorization": token}
        if self.x_api_key:
            headers["X-API-Key"] = self.x_api_key
        return headers

    def _build_payload(
        self,
        json: dict[str, Any] | None,
        method: str,
        skip_checksum: bool,
    ) -> dict[str, Any] | None:
        if json is None:
            return None
        payload = dict(json)
        if not skip_checksum and method.upper() in {"POST", "PUT", "PATCH"} and self.x_api_key:
            if "checksum" not in payload:
                payload["checksum"] = SecurityManager.create_checksum(self.x_api_key, payload)
        return payload

    def _build_url(self, endpoint: str, base_url: str | None) -> str:
        return f"{base_url or self.base_url}/{endpoint.lstrip('/')}"
