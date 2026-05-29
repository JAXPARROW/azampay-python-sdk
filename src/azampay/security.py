from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


class SecurityManager:
    """HMAC-SHA256 checksum utilities for AzamPay request signing."""

    @staticmethod
    def create_checksum(checksum_key: str, payload: dict[str, Any]) -> str:
        """Return a 64-char HMAC-SHA256 hex digest for *payload*.

        Keys are sorted recursively before serialisation so the checksum is
        deterministic regardless of insertion order.  Returns an empty string
        when *checksum_key* is falsy.
        """
        if not checksum_key:
            return ""
        canonical = SecurityManager._canonicalize(payload)
        body = json.dumps(canonical, separators=(",", ":"), ensure_ascii=False)
        return hmac.new(checksum_key.encode(), body.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def verify_webhook(checksum_key: str, payload: dict[str, Any], signature: str) -> bool:
        """Return True when *signature* matches the expected checksum for *payload*."""
        if not checksum_key or not signature:
            return False
        expected = SecurityManager.create_checksum(checksum_key, payload)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def _canonicalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: SecurityManager._canonicalize(v) for k in sorted(obj) for v in (obj[k],)}
        if isinstance(obj, list):
            return [SecurityManager._canonicalize(item) for item in obj]
        return obj
