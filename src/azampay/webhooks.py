from __future__ import annotations

from typing import Any

from .security import SecurityManager


class WebhookValidator:
    """Helper for verifying AzamPay callback signatures in web frameworks."""

    @staticmethod
    def verify(payload: dict[str, Any], signature: str, checksum_key: str) -> bool:
        """Return True when *signature* is a valid HMAC-SHA256 digest of *payload*."""
        return SecurityManager.verify_webhook(checksum_key, payload, signature)
