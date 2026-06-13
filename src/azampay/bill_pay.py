from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


class BillPayValidator:
    """Utilities for implementing AzamPay Bill Pay merchant endpoints.

    AzamPay calls YOUR server on three endpoints you host:
      - POST /api/merchant/name-lookup
      - POST /api/merchant/payment
      - POST /api/merchant/status-check

    This class verifies that incoming requests are authentic and builds
    correctly-shaped response dicts to return to AzamPay.

    Hash algorithm (name-lookup and payment only)::

        canonical = json.dumps(Data, separators=(',', ':'))
        sha256_bytes = sha256(canonical.encode()).digest()
        hash = hmac_sha256(secret, sha256_bytes).hexdigest()

    The ``status-check`` endpoint sends only ``MerchantReferenceId`` with no hash.
    """

    @staticmethod
    def verify_hash(data: dict[str, Any], hash_str: str, secret: str) -> bool:
        """Verify the HMAC-SHA256 hash on an incoming name-lookup or payment request.

        Args:
            data:     The ``Data`` object from the incoming request body (parsed JSON).
            hash_str: The ``Hash`` field from the incoming request body.
            secret:   The shared secret key provided by AzamPay.

        Returns:
            True if the hash is valid, False otherwise.
        """
        if not secret or not hash_str:
            return False
        canonical = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        sha256_bytes = hashlib.sha256(canonical.encode("utf-8")).digest()
        expected = hmac.new(
            secret.encode("utf-8"), sha256_bytes, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, hash_str)

    @staticmethod
    def name_lookup_response(
        name: str,
        bill_amount: float,
        bill_identifier: str,
        status: str = "Success",
        message: str = "Name found for the provided BillIdentifier.",
        status_code: int = 0,
    ) -> dict[str, Any]:
        """Build a Name Lookup API response to return to AzamPay.

        Args:
            name:            Account holder name (e.g. "John Doe").
            bill_amount:     Outstanding bill amount.
            bill_identifier: The identifier from the incoming request.
            status:          Status string (default "Success").
            message:         Human-readable result message.
            status_code:     Numeric status code (0 = success).

        Returns:
            Dict matching the Name Lookup API response schema.
        """
        return {
            "Name": name,
            "BillAmount": bill_amount,
            "BillIdentifier": bill_identifier,
            "Status": status,
            "Message": message,
            "StatusCode": status_code,
        }

    @staticmethod
    def payment_response(
        merchant_reference_id: str,
        status: str = "Success",
        message: str = "Payment successful.",
        status_code: int = 0,
    ) -> dict[str, Any]:
        """Build a Payment API response to return to AzamPay.

        Args:
            merchant_reference_id: Your unique reference ID for this transaction.
            status:                Status string (default "Success").
            message:               Human-readable result message.
            status_code:           Numeric status code (0 = success).

        Returns:
            Dict matching the Payment API response schema.
        """
        return {
            "MerchantReferenceId": merchant_reference_id,
            "Status": status,
            "Message": message,
            "StatusCode": status_code,
        }

    @staticmethod
    def status_check_response(
        merchant_reference_id: str,
        status: str,
        message: str = "",
        status_code: int = 0,
    ) -> dict[str, Any]:
        """Build a Status Check API response to return to AzamPay.

        Args:
            merchant_reference_id: The reference ID from the incoming request.
            status:                Current transaction status (e.g. "Success", "Pending", "Failed").
            message:               Human-readable result message.
            status_code:           Numeric status code (0 = success).

        Returns:
            Dict matching the Status Check API response schema.
        """
        return {
            "MerchantReferenceId": merchant_reference_id,
            "Status": status,
            "Message": message,
            "StatusCode": status_code,
        }
