from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ._base_client import BaseClient
from ._constants import _RETRY_STATUSES
from ._http import handle_response, safe_json
from .exceptions import AzamPayError, AuthenticationError, ForbiddenError


async def _backoff(attempt: int) -> None:
    await asyncio.sleep(2 ** (attempt - 1))


class AsyncAzamPayClient(BaseClient):
    """Asynchronous AzamPay API client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lock: asyncio.Lock | None = None
        self._http = httpx.AsyncClient(timeout=self.timeout)

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    async def _authenticate(self) -> str:
        async with self._get_lock():
            if self._token and time.monotonic() < self._token_expires_at:
                return self._token

            last_exc: Exception | None = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = await self._http.post(self._auth_endpoint(), json=self._auth_payload())
                except httpx.TransportError as exc:
                    last_exc = exc
                    if attempt < self.max_retries:
                        await _backoff(attempt)
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
                    await _backoff(attempt)
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

    async def request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
        skip_checksum: bool = False,
    ) -> Any:
        token = await self._authenticate()
        headers = self._build_headers(token)
        payload = self._build_payload(json, method, skip_checksum)
        url = self._build_url(endpoint, base_url)
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await self._http.request(method, url, json=payload, params=params, headers=headers)
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    await _backoff(attempt)
                continue

            if resp.status_code in _RETRY_STATUSES and attempt < self.max_retries:
                body = safe_json(resp)
                last_exc = AzamPayError(
                    body.get("message", "Server error"), status_code=resp.status_code, response=body
                )
                await _backoff(attempt)
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

    async def is_healthy(self) -> bool:
        """Return True if the API is reachable and credentials are valid."""
        try:
            await self._authenticate()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    def __repr__(self) -> str:
        env = "sandbox" if self.sandbox else "production"
        return f"{type(self).__name__}(app_name={self.app_name!r}, env={env!r})"

    async def __aenter__(self) -> "AsyncAzamPayClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
