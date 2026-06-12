from __future__ import annotations

import base64
import hashlib
import hmac
import json
from functools import lru_cache
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


@lru_cache(maxsize=8)
def _load_rsa_public_key(pem: str) -> RSAPublicKey:
    return serialization.load_pem_public_key(pem.encode())  # type: ignore[return-value]


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
    def create_rsa_checksum(public_key_pem: str, input_string: str) -> str:
        """Return Base64(RSA_ENCRYPT(SHA512(input_string))) for disbursement signing.

        Disbursement input: sourceAcc+destAcc+currency+amount+epochDate+externalReferenceId
        Name lookup input:  bankName+accountNumber
        """
        sha512_digest = hashlib.sha512(input_string.encode("utf-8")).digest()
        public_key = _load_rsa_public_key(public_key_pem)
        encrypted = public_key.encrypt(sha512_digest, padding.PKCS1v15())
        return base64.b64encode(encrypted).decode()

    @staticmethod
    def _canonicalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: SecurityManager._canonicalize(obj[k]) for k in sorted(obj)}
        if isinstance(obj, list):
            return [SecurityManager._canonicalize(item) for item in obj]
        return obj
