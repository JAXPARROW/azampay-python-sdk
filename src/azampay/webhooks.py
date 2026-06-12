from __future__ import annotations

import base64
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from .security import SecurityManager, _load_rsa_public_key


class WebhookValidator:
    """Helper for verifying AzamPay callback signatures in web frameworks."""

    @staticmethod
    def verify(payload: dict[str, Any], signature: str, checksum_key: str) -> bool:
        """Verify an HMAC-SHA256 callback signature (legacy / non-RSA integrations).

        Returns True when *signature* matches the HMAC-SHA256 digest of *payload*.
        """
        return SecurityManager.verify_webhook(checksum_key, payload, signature)

    @staticmethod
    def verify_callback_signature(
        utility_ref: str,
        external_reference: str,
        transaction_status: str,
        operator: str,
        signature_b64: str,
        public_key_pem: str,
    ) -> bool:
        """Verify the RSA-SHA256 signature on an AzamPay checkout callback.

        AzamPay signs the concatenated string
        ``{utilityref}{externalreference}{transactionstatus}{operator}``
        with their RSA private key (SHA-256, PKCS#1 v1.5).

        Fetch the public key once via ``CheckoutService.get_public_key()`` and
        cache it locally; refresh every 24 hours or on verification failure.

        Args:
            utility_ref:        ``utilityref`` field from the callback payload.
            external_reference: ``externalreference`` field from the callback payload.
            transaction_status: ``transactionstatus`` field from the callback payload.
            operator:           ``operator`` field from the callback payload.
            signature_b64:      ``signature`` field (base64-encoded) from the callback payload.
            public_key_pem:     AzamPay RSA public key in PEM format.

        Returns:
            True if the signature is valid, False otherwise.
        """
        data = (
            f"{utility_ref}{external_reference}{transaction_status}{operator}"
        ).encode("utf-8")
        try:
            sig = base64.b64decode(signature_b64)
            public_key = _load_rsa_public_key(public_key_pem)
            public_key.verify(sig, data, padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            return False
