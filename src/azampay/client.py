from __future__ import annotations

import threading
import time
from typing import Any

import httpx

from ._base_client import BaseClient
from ._constants import _RETRY_STATUSES
from ._http import handle_response, safe_json
from .exceptions import AzamPayError, AuthenticationError, ForbiddenError


def _backoff(attempt: int) -> None:
    time.sleep(2 ** (attempt - 1))


class AzamPayClient(BaseClient):
    """Synchronous AzamPay API client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()
        self._http = httpx.Client(timeout=self.timeout)

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
                    resp = self._http.post(self._auth_endpoint(), json=self._auth_payload())
                except httpx.TransportError as exc:
                    last_exc = exc
                    if attempt < self.max_retries:
                        _backoff(attempt)
                    continue

                body = safe_json(resp)

                if resp.status_code == 401:
                    raise AuthenticationError(
                        body.get("message", "Authentication failed"), status_code=401, response=body
                    )
                if resp.status_code == 403:
                    raise ForbiddenError(
                        body.get("message", "Forbidden"), status_code=403, response=body
                    )
                if resp.status_code in _RETRY_STATUSES and attempt < self.max_retries:
                    last_exc = AzamPayError(
                        body.get("message", "Server error"), status_code=resp.status_code, response=body
                    )
                    _backoff(attempt)
                    continue

                if not resp.is_success or not body.get("success", True):
                    raise AzamPayError(
                        body.get("message", "Token generation failed"),
                        status_code=resp.status_code,
                        response=body,
                    )

                self._token = f"Bearer {body['data']['accessToken']}"
                self._token_expires_at = self._parse_token_expiry(body)
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
        headers = self._build_headers(token)
        payload = self._build_payload(json, method, skip_checksum)
        url = self._build_url(endpoint, base_url)
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._http.request(method, url, json=payload, params=params, headers=headers)
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                continue

            if resp.status_code in _RETRY_STATUSES and attempt < self.max_retries:
                body = safe_json(resp)
                last_exc = AzamPayError(
                    body.get("message", "Server error"), status_code=resp.status_code, response=body
                )
                _backoff(attempt)
                continue

            return handle_response(resp)

        raise (
            last_exc
            if isinstance(last_exc, AzamPayError)
            else AzamPayError(str(last_exc), response={})
        )

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

    def __enter__(self) -> "AzamPayClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
